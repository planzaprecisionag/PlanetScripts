#%%
import pl_spatial_utils as psu
import os

#%% Testing dir walk
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldAOIsForPlanetDownload\Field05PolygonCoords_GeoJSON.geojson'

raster_files_covering_the_aoi = []

for path, subdirs, files in os.walk(raster_root_dir):
    print('Path:{}'.format(path))
    print('Subdirs:{}'.format(subdirs))
    for f in files:
        if f.endswith('_SR_clip.tif'):
            print('Raster:{}'.format(f))

#%%
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\Field5PolygonCoords_GeoJSON_epsg32618_correct.geojson'
raster_file_ending = '_SR_clip.tif'

raster_files_covering_the_aoi = []

for path, subdirs, files in os.walk(raster_root_dir):
    for f in files:
        if f.endswith(raster_file_ending):
            file_path = os.path.join(path, f)
            if psu.check_if_raster_intersects_vector(file_path, field_aoi_file_path):
                raster_files_covering_the_aoi.append(file_path)

# raster_files_covering_the_aoi = raster_files_covering_the_aoi.sort()
print(raster_files_covering_the_aoi)


# %% debugging org vector issue
from osgeo import gdal, ogr, osr
gdal.UseExceptions()

raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
# field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldAOIsForPlanetDownload\Field05PolygonCoords_GeoJSON.geojson'
field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\Field5PolygonCoords_GeoJSON_epsg32618_correct.geojson'
raster_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3\5516798d-a973-4b24-bb5d-e81cd3ffb698\PSScene\20220918_154730_74_2414_3B_AnalyticMS_SR_clip_ndvi.tif'
vector_file_path = field_aoi_file_path

vector = ogr.Open(vector_file_path)
raster = gdal.Open(raster_file_path)

if raster is None:
    print('Could not open file at {}'.format(raster_file_path))
else:
    raster_proj = raster.GetProjection()
    srs = osr.SpatialReference(wkt=raster_proj)
    # if srs.IsProjected:
    #     print(srs.GetAttrValue('projcs'))
    # print(srs.GetAttrValue('geogcs'))
    # print(srs.GetAttrValue('authority', 1))
    raster_crs = srs.GetAttrValue('authority', 1)

if vector is None:
    print('Could not open file at {}'.format(vector_file_path))
else:
    layer = vector.GetLayer()
    feature = layer.GetNextFeature()
    geo = feature.GetGeometryRef()
    spatialRef = geo.GetSpatialReference()
    vector_crs = str(spatialRef.GetAttrValue('authority', 1))
    # vector_crs = str(spatialRef.GetAuthorityCode('PROJCS'))

print('Raster CRS: {}'.format(raster_crs))
print('Vector CRS: {}'.format(vector_crs))


# %% TESTING FXN TO RETURN SORTED (BY DATE, ASC) LIST OF RASTERS BY AOI VECTOR

raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\Field5PolygonCoords_GeoJSON_epsg32618_correct.geojson'
raster_file_ending = '_SR_clip.tif'

# first, test fxn that returns list of rasters by aoi (without sort)
rasters_in_aoi_unsorted = psu.get_rasters_by_aoi_vector(field_aoi_file_path, raster_root_dir, raster_file_ending, recursive_search=True, sort_list=False)

# next, test same fxn with sort
rasters_in_aoi_unsorted_asc = psu.get_rasters_by_aoi_vector(field_aoi_file_path, raster_root_dir, raster_file_ending, recursive_search=True, sort_list=True)

# next, test sort fxn sorting descending
rasters_in_aoi_unsorted_desc = psu.sort_planet_rasters_by_date(rasters_in_aoi_unsorted, sort_descending=True)

# %%
