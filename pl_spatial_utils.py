#%%
from osgeo import gdal, ogr, osr
gdal.UseExceptions()
import os
from collections import OrderedDict
import rasterio
import geopandas as gp

# %%
# NOTE: be sure to set GDAL objects to none when done to 
# dereference so that updates can be written and the file closed

#%% determine if raster intersects vector 
# ie - is field within raster file, so we can organize rasters
# or process rasters by field , etc
# code adapted from: https://gis.stackexchange.com/questions/126467/determining-if-shapefile-and-raster-overlap-in-python-using-ogr-gdal
def check_if_raster_intersects_vector(raster_file_path, vector_file_path):
    raster = gdal.Open(raster_file_path)
    vector = ogr.Open(vector_file_path)

    #check to ensure that both are in the same crs
    if not check_for_same_crs(raster, vector):
        print('ERROR: CRS values not the same for both files')
        return False

    # Get raster geometry
    transform = raster.GetGeoTransform()
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    xLeft = transform[0]
    yTop = transform[3]
    xRight = xLeft+cols*pixelWidth
    yBottom = yTop+rows*pixelHeight 
    # note: may need to change the above for locations in the southern hemisphere to 
    # yBottom = yTop-abs(rows*pixelHeight)

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xLeft, yTop)
    ring.AddPoint(xLeft, yBottom)
    ring.AddPoint(xRight, yBottom)
    ring.AddPoint(xRight, yTop)
    ring.AddPoint(xLeft, yTop)
    rasterGeometry = ogr.Geometry(ogr.wkbPolygon)
    rasterGeometry.AddGeometry(ring)

    # Get vector geometry
    layer = vector.GetLayer()
    feature = layer.GetFeature(0)
    vectorGeometry = feature.GetGeometryRef()

    raster_intersects_vector = rasterGeometry.Intersect(vectorGeometry)

    raster = None
    vector = None

    return raster_intersects_vector

def check_if_raster_intersects_points(raster_file_path:str, point_coords:list):
    # adapted from code sample at: https://stackoverflow.com/questions/67893343/how-to-raise-an-error-that-coordinates-are-out-of-raster-bounds-rasterio-sample
    # NOTE: raster and points must be in same CRS
    intersects = False
    with rasterio.open(raster_file_path) as raster:
        # loop through points list, return True (ie point intersects with
        # raster) if any point in list intersects with raster
        for x, y in point_coords:
            row, col = raster.index(x,y)
            if not any([row<0, col<0, row >= raster.height, col >= raster.width]):
                intersects = True
    
    return intersects

def check_for_same_crs(gdal_raster, ogr_vector):
    if gdal_raster is None:
        return False
    else:
        raster_proj = gdal_raster.GetProjection()
        srs = osr.SpatialReference(wkt=raster_proj)
        # if srs.IsProjected:
        #     print(srs.GetAttrValue('projcs'))
        # print(srs.GetAttrValue('geogcs'))
        # print(srs.GetAttrValue('authority', 1))
        raster_crs = str(srs.GetAttrValue('authority', 1))

    if ogr_vector is None:
        return False
    else:
        layer = ogr_vector.GetLayer()
        feature = layer.GetNextFeature()
        geo = feature.GetGeometryRef()
        spatialRef = geo.GetSpatialReference()
        vector_crs = str(spatialRef.GetAttrValue('authority', 1))

    return raster_crs == vector_crs

def get_rasters_by_aoi_vector(aoi_file_path, raster_root_dir, raster_file_ending, 
    recursive_search=True, sort_list=True):
    raster_files_covering_the_aoi = []

    if recursive_search:
        for path, subdirs, files in os.walk(raster_root_dir):
            for f in files:
                if f.endswith(raster_file_ending):
                    file_path = os.path.join(path, f)
                    if check_if_raster_intersects_vector(file_path, aoi_file_path):
                        raster_files_covering_the_aoi.append(file_path)
    else:
        for f in os.listdir(raster_root_dir):
            if f.endswith(raster_file_ending):
                file_path = os.path.join(raster_root_dir, f)
                if check_if_raster_intersects_vector(file_path, aoi_file_path):
                    raster_files_covering_the_aoi.append(file_path)

    # raster_files_covering_the_aoi = sorted(raster_files_covering_the_aoi)

    if sort_list:
        raster_files_covering_the_aoi = sort_planet_rasters_by_date(raster_files_covering_the_aoi)
    
    return raster_files_covering_the_aoi

def get_rasters_by_points(points_file_path, raster_root_dir, raster_file_ending, 
    group_id_col_name, point_id_col_name, recursive_search=True, sort_list=True):

    # load file into gdf
    gdf_all_points = gp.read_file(points_file_path)
    #group all points gdf by farm name
    grp_all_pts_by_entity = gdf_all_points.groupby(group_id_col_name)

    entity_raster_dict = {}
    entity_points_dict = {}
    #loop through groups of points by group (ex farm) and get rasters belonging to that
    for name, group in grp_all_pts_by_entity:
        raster_files_covering_the_aoi = []
        print('Processing points and rasters for: {}'.format(name))
        group_points = group[0:].geometry
        group_point_ids = group[0:][point_id_col_name]
        group_xys = list(zip(group_points.x.tolist(), group_points.y.tolist()))
        # add key of entityname:point coords to dict
        entity_points_dict[name] = list(zip(group_point_ids, group_xys))
        
        if recursive_search:
            for path, subdirs, files in os.walk(raster_root_dir):
                for f in files:
                    if f.endswith(raster_file_ending):
                        file_path = os.path.join(path, f)
                        if check_if_raster_intersects_points(file_path, group_xys):
                            raster_files_covering_the_aoi.append(file_path)
        else:
            for f in os.listdir(raster_root_dir):
                if f.endswith(raster_file_ending):
                    file_path = os.path.join(raster_root_dir, f)
                    if check_if_raster_intersects_points(file_path, group_xys):
                        raster_files_covering_the_aoi.append(file_path)

        # raster_files_covering_the_aoi = sorted(raster_files_covering_the_aoi)

        if sort_list:
            raster_files_covering_the_aoi = sort_planet_rasters_by_date(raster_files_covering_the_aoi)

        # add entity's key to dict with list of rasters intersecting its points
        entity_raster_dict[name] = raster_files_covering_the_aoi

    print('Processing Complete')
    return entity_points_dict, entity_raster_dict

def sort_planet_rasters_by_date(planet_raster_filepaths, sort_descending=False):
    raster_dict = {}
    for r in planet_raster_filepaths:
        file_name = os.path.basename(r)
        raster_dict[file_name] = r

    # now sort the dict by key, which is the filename, it starts with the date, so no need to 
    # extract date etc 
    sorted_rasters = OrderedDict(sorted(raster_dict.items(), reverse=sort_descending, key=lambda t: t[0]))

    return sorted_rasters


