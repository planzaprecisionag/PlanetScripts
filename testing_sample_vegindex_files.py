#%% lib imports
import os
import pl_spatial_utils as plsu
import geopandas as gp

#%% Testing fnx to determine if points fall within raster
points_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\SamplePoints\OFEBiologicalsSurveyPoints_EPSG32618.geojson'
test_farm_name = 'Curc 32B'
test_farm2_name = 'Underwood'
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\Field5PolygonCoords_GeoJSON_epsg32618_correct.geojson'
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
#%% testing fxn to return list of raster filepaths intersecting points for a farm
points_file_path = r''
test_farm_name = 'Curc 32B'
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\Field5PolygonCoords_GeoJSON_epsg32618_correct.geojson'
raster_file_ending = '_SR_clip.tif'