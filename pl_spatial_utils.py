#%%
from osgeo import gdal, ogr, osr
gdal.UseExceptions()

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