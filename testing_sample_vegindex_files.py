#%% lib imports
import os
import pl_spatial_utils as plsu
import geopandas as gp
import pl_raster_sampler_lib as plrsl

#%% Testing fnx to determine if points fall within raster
points_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\SamplePoints\OFEBiologicalsSurveyPoints_EPSG32618.geojson'
test_farm_name = 'Curc 32B'
test_farm2_name = 'Underwood'
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
raster_file_ending = '_SR_clip.tif'
farm_id_col_name = 'Farm Name'
sample_id_col_name = 'Sample ID'

gdf_all_points = gp.read_file(points_file_path)

#get distinct farm names, sorted asc
farm_names = sorted(gdf_all_points[farm_id_col_name].unique())

#group all points gdf by farm name
grp_all_pts_by_farm = gdf_all_points.groupby(farm_id_col_name)

test_points = []
test_points2 = []
for name, group in grp_all_pts_by_farm:
    print(name)
    group_points = group[0:].geometry
    group_xys = list(zip(group_points.x.tolist(), group_points.y.tolist()))
    print(group_xys)
    print()
    if name == test_farm_name:
        test_points = group_xys
    
    if name == test_farm2_name:
        test_points2 = group_xys

#%% Test raster point intersection check fnx
test_raster_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3\5516798d-a973-4b24-bb5d-e81cd3ffb698\PSScene\20220918_154730_74_2414_3B_AnalyticMS_SR_clip_msavi.tif'
intersects = plsu.check_if_raster_intersects_points(test_raster_path, test_points)
print('Intersects: {}'.format(str(intersects)))

intersects2 = plsu.check_if_raster_intersects_points(test_raster_path, test_points2)
print('Intersects2: {}'.format(str(intersects2)))

#%% testing fxn to return list of raster filepaths intersecting points for sample points
# grouped by farm
points_file_path = rpoints_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\SamplePoints\OFEBiologicalsSurveyPoints_EPSG32618.geojson'
test_farm_name = 'Curc 32B'
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
# raster_file_ending = '_SR_clip.tif'
raster_file_endings = ['_evi.tif', '_msavi.tif', '_ndvi.tif']
farm_id_col_name = 'Farm Name'
sample_id_col_name = 'Sample ID'

# below returns two dicts:
# {key, [point_x, point_y]}
#  {'key', ordered_dict{fname, filepath}}
pts_dict, rasters_dict = plsu.get_rasters_by_points(points_file_path, raster_root_dir, 
raster_file_endings, farm_id_col_name, sample_id_col_name, recursive_search=True,  
sort_list=True)

#%% Check dicts for valid data
test_farm_pts_dict = pts_dict['Blodgett #1']
test_farm_rasters_dict = rasters_dict['Blodgett #1']

test_farm_pts_dict
test_farm_rasters_dict

#%%
for key in rasters_dict:
    print('{}: {}'.format(key, str(len(rasters_dict[key]))))

#%% 
for key in pts_dict:
    print('{}: {}'.format(key, str(len(pts_dict[key]))))

# %% Sample Planet rasters by points 
# TODO: use _udm files for pixel-level data quality checks
# for now, just sample, will add that once this is working

points_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\SamplePoints\OFEBiologicalsSurveyPoints_EPSG32618.geojson'
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
raster_file_ending = '_SR_clip.tif'
farm_id_col_name = 'Farm Name'
sample_id_col_name = 'Sample ID'

gdf_all_points = gp.read_file(points_file_path)

#get distinct farm names, sorted asc
farm_names = sorted(gdf_all_points[farm_id_col_name].unique())

#group all points gdf by farm name
grp_all_pts_by_farm = gdf_all_points.groupby(farm_id_col_name)
# use groubyobject.get_group[name] to retrieve df for one entity

# keys in rasters and points dicts are the same, so loop through dict.keys and 
# access elements or both by current key
for key in pts_dict:
    print(key)
    point_data = pts_dict[key]
    raster_paths = rasters_dict[key].values

    # get gdf of data for the current key (which is the current farm)
    gdf_entity_data = grp_all_pts_by_farm.get_group(key)

    # now loop through the points and sample the rasters.
    # can I do this via an apply to be more efficient?
    # site_sample_point_coords = []
    # for sample_id, coords in point_data:
    #     # print(sample_id)
    #     # print(coords)
    #     # x = coords[0]
    #     # y = coords[1]
    #     site_sample_point_coords.append(coords)

    # print(site_sample_point_coords)
    # point data example:
    # [
    #   ('PB-A', (408144.2894986458, 4721894.268953732)), 
    #   ('PB-B', (408267.38148685277, 4722057.913568075)), 
    #   ('CTRL-A', (408179.33620043367, 4722391.282174873)), 
    #   ('CTRL-B', (408129.8303141982, 4722451.375608475))
    # ]

    # TODO resume coding here:
    # pass key,  point_data to fxn to make gdf then sample by points ala pl_rslib.samplebypoints


# %%  Testing planet ofe biologicals raster sampler fxn
for key in rasters_dict:
    # key is farm name, raster_paths is odict values of raster paths
    raster_file_paths = rasters_dict[key]

    # get gdf of data for the current key (which is the current farm)
    gdf_entity_data = grp_all_pts_by_farm.get_group(key)

#%% reload plrsl lib
import importlib
importlib.reload(plrsl)

# %% Testing inner sampler function using Underwood (last key in rasters dict)
# for fname_key in raster_file_paths:
#     print(raster_file_paths[fname_key])
bands_to_sample = [1]
gdfTest = plrsl.sample_rasters_by_points(raster_file_paths, gdf_entity_data, bands_to_sample)

#%% reload plrsl lib
import importlib
importlib.reload(plrsl)

# %% Test running planet ofe biological raster sampler
bands_to_sample = [1]
farm_id_col_name = 'Farm Name'
gdf_all_raster_samples = plrsl.sample_rasters_by_points_planet_ofe_biological(
    rasters_dict, gdf_all_points, bands_to_sample, farm_id_col_name
)


# %% Write raster sample data to csv file
out_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\SampledRasterData\OFEBiological_Planet_VI_Point_Samples.csv'
gdf_all_raster_samples.to_csv(out_file_path)
# %%
