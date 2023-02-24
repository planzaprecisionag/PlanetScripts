# script to generate vi maps for fields for a specific date
# ex: NDVI at date corresponding to tasseling for Pankow

#%% 
# import libs
import pl_spatial_utils as psu
import importlib

#%%
# reload pl spatial utils lib to load changes
importlib.reload(psu)

#%%
# get list of rasters for a field
field_name = 'Pankow'
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
# Pankow
field_aoi_file_path = r'C:/Users/P/Box/Phillip/OFE Biologicals/QGIS/FieldPolygons/Field11PolygonCoords_GeoJSON_epsg32618.geojson'
# Branton 18-20
# field_aoi_file_path = r'C:/Users/P/Box/Phillip/OFE Biologicals/QGIS/FieldPolygons/Field9PolygonCoords_GeoJSON_epsg32618.geojson'
# Branton 406
# field_aoi_file_path = r'C:/Users/P/Box/Phillip/OFE Biologicals/QGIS/FieldPolygons/Field10PolygonCoords_GeoJSON_epsg32618.geojson'

raster_file_ending = '_ndvi.tif'
# raster_file_ending = '_SR_clip.tif'

field_rasters = psu.get_rasters_by_aoi_vector(field_aoi_file_path, raster_root_dir, raster_file_ending, recursive_search=True, sort_list=True)

print('Files found: {}'.format(len(field_rasters)))

#%%
# show rasters covering the specified field
for key in field_rasters:
    print(key)
    print(field_rasters[key])
    print('Now, load these files into QGIS until I integrate this with the  mapping library from env data project ')

# %%
