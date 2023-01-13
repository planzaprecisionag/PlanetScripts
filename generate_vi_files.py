#%%
import pl_vegetation_index_lib as plvi
import pl_spatial_utils as plsu
import os

#%% Set Param Values
indices_to_calculate = [
    'ndvi', 
    'evi',
    'msavi'
    ]

band_mappings = {
    "blue": 1,
    "green": 2,
    "red": 3,
    "nir": 4
}

raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
raster_file_ending = '_SR_clip.tif'
aoi_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons'
aoi_file_ending = 'epsg32618.geojson'

#%% Generate vegetation index files

# dict to hold field:[raster files]
aoi_raster_dict = {}

# loop through field aoi files
for f in os.listdir(aoi_dir):
    if f.endswith(aoi_file_ending):
        # get list of rasters covering the field
        aoi_file_path = os.path.join(aoi_dir, f)
        rasters = plsu.get_rasters_by_aoi_vector(aoi_file_path, raster_root_dir, raster_file_ending, 
            recursive_search=True, sort_list=True)
        
        # persist field_aoi and associated raster list
        aoi_raster_dict[f] = rasters

        # generate vegetation index rasters for each planet raster covering the current field's aoi
        for r in rasters.values():
            print('Generating veg index rasters for {}'.format(r))
            plvi.generate_vegetation_index_rasters(r, indices_to_calculate, band_mappings)
            print()

print('****** DONE ********')

# %% test getting  list of raster files by field aoi vectors
for f in os.listdir(aoi_dir):
    if f.endswith(aoi_file_ending):
        # get list of rasters covering the field
        aoi_file_path = os.path.join(aoi_dir, f)
        rasters = plsu.get_rasters_by_aoi_vector(aoi_file_path, raster_root_dir, raster_file_ending, 
            recursive_search=True, sort_list=True)
        
        # persist field_aoi and associated raster list
        aoi_raster_dict[f] = rasters

#%% testing iterating through dict key values (contains ordered dict)
for f in aoi_raster_dict['Field6PolygonCoords_GeoJSON_epsg32618.geojson']:
    print(f)

# %% manual fix to generate vi files for field 5
# fpath = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\Field5PolygonCoords_GeoJSON_epsg32618.geojson'
# rasters = plsu.get_rasters_by_aoi_vector(fpath, raster_root_dir, raster_file_ending, 
#             recursive_search=True, sort_list=True)
# for r in rasters.values():
#     print('Generating veg index rasters for {}'.format(r))
#     plvi.generate_vegetation_index_rasters(r, indices_to_calculate, band_mappings)
#     print()
# print('DONE')