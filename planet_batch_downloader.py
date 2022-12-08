#%% Library imports
import os
from planet_raster_downloader import get_planet_download_stats, download_planet_rasters
import planet_credentials as plc
import planet_json_utils as pju

#%% Getting param values to pass to stats and dl fxns
# TODO: make form to capture these values
download_save_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\2022'
item_types = ['PSScene']
asset_type = 'ortho_analytic_4b_sr'
planet_api_key = plc.get_planet_api_key()
planet_base_url = "https://api.planet.com/data/v1"
img_start_date_string = "2022-04-01T00:00:00.000Z"
img_end_date_string = "2022-10-31T00:00:00.000Z"
cloud_cover_percent_max = 0.8
interval_type = 'day'

# root dir holding field boundary polygons. will loop through this and pull
# planet rasters using these as AOI's
field_aoi_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldAOIsForPlanetDownload'

#%% CHECK STATS FOR SEARCH (how many images, etc)
# loop through all field aoi polygon files in aoi dir
print('Be sure that AOI polygons are epsg:4326, NOT a projected CRS')
is_first_file = True
for f in os.listdir(field_aoi_dir):
    aoi_file = os.path.join(field_aoi_dir, f)
    # print('AOI File: {}'.format(aoi_file))
    if os.path.isfile(aoi_file) and f.endswith('.geojson'):
        # print(f)
        field_aoi = pju.extract_geometry_from_geojson_file(aoi_file)
        # print(field_aoi)
        if is_first_file:
            get_planet_download_stats(download_save_dir, item_types, field_aoi, 
                asset_type, planet_api_key, planet_base_url, img_start_date_string,
                img_end_date_string, cloud_cover_percent_max, interval_type)
            is_first_file = False

#%% DOWNLOAD IMAGERY
# loop through all field aoi polygon files in aoi dir
print('Be sure that AOI polygons are epsg:4326, NOT a projected CRS')
# TESTING - only process one field for now
print('TEST MODE: ONLY PROCESSING ONE FIELD')
is_first_field = True
for f in os.listdir(field_aoi_dir):
    aoi_file = os.path.join(field_aoi_dir, f)
    # print('AOI File: {}'.format(aoi_file))
    if os.path.isfile(aoi_file) and f.endswith('.geojson'):
        # print(f)
        field_aoi = pju.extract_geometry_from_geojson_file(aoi_file)
        # print(field_aoi)
        if is_first_field:
            download_planet_rasters(download_save_dir, item_types, field_aoi, 
                asset_type, planet_api_key, planet_base_url, img_start_date_string,
                img_end_date_string, cloud_cover_percent_max, really_download_images=True, 
                overwrite_existing=False)
            # print('should only see this once')
            is_first_field = False


#%% DEBUGGING ####
from planet_raster_downloader import get_combined_search_filter, get_date_filter, get_geom_filter, get_property_range_filter

startf = get_date_filter('lte', img_end_date_string)
endf = get_date_filter('gte', img_start_date_string)
geof = get_geom_filter(field_aoi)
cloudf = get_property_range_filter('cloud_cover', 'lte', cloud_cover_percent_max)
allf = [startf, endf, geof, cloudf]
combinedf = get_combined_search_filter(allf)

print(allf)
# %%
