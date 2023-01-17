#%% lib imports
import os
import pl_spatial_utils as plsu
import geopandas as gp

#%% Testing fnx to determine if points fall within raster
points_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\SamplePoints\OFEBiologicalsSurveyPoints_EPSG32618.geojson'
test_farm_name = 'Curc 32B'
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

for name, group in grp_all_pts_by_farm:
    print(name)
    group_points = group[0:].geometry
    group_xys = list(zip(group_points.x.tolist(), group_points.y.tolist()))
    print(group_xys)
    print()

# all_points = gdf_all_points[0:].geometry
# all_xys = list(zip(all_points.x.tolist(), all_points.y.tolist()))


#%% testing fxn to return list of raster filepaths intersecting points for a farm
points_file_path = r''
test_farm_name = 'Curc 32B'
raster_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
field_aoi_file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\Field5PolygonCoords_GeoJSON_epsg32618_correct.geojson'
raster_file_ending = '_SR_clip.tif'