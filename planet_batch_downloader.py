#%% Library imports
import os
from planet_raster_downloader import get_planet_download_stats, download_planet_rasters, search_planet
import planet_credentials as plc
import planet_json_utils as pju
from planet_raster_downloader_v2 import order_and_download_clipped_rasters, download_order
import asyncio
#fix issue with asyncio running in VSode ipython
import nest_asyncio
nest_asyncio.apply()

# %%

#%% Getting param values to pass to stats and dl fxns
# TODO: make form to capture these values
download_save_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\2022'
item_types = ['PSScene']
asset_type = 'ortho_analytic_4b_sr'
planet_api_key = plc.get_planet_api_key()
planet_base_url = "https://api.planet.com/data/v1"
img_start_date_string = "2022-05-09T00:00:00.000Z"
# img_end_date_string = "2022-10-31T00:00:00.000Z"
img_end_date_string = "2022-06-08T00:00:00.000Z"
# see https://developers.planet.com/docs/data/psscene/ for property filters
# cloud_cover_percent_max = 0.8
clear_percent = 30 #% of area not impacted by cloud, haze, shadow, or snow
interval_type = 'year'

# root dir holding field boundary polygons. will loop through this and pull
# planet rasters using these as AOI's
field_aoi_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldAOIsForPlanetDownload'

#%% CHECK STATS FOR SEARCH (how many images, etc)
# loop through all field aoi polygon files in aoi dir
print('Be sure that AOI polygons are epsg:4326, NOT a projected CRS')
is_first_file = True
if is_first_file:
    print('TEST MODE: Only processing first field file')
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
                img_end_date_string, clear_percent, interval_type)
            is_first_file = False

#%% SEARCH AND SHOW RESULTS RESPONSE 
# return list of asset id's that will be sent to the order
# and clip api's to download the clipped imagery that way, replacing the 
# planet_raster_downloader fxn
field_aoi_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\CombinedAOIsForPlanet100kmMinDownload'
print('Be sure that AOI polygons are epsg:4326, NOT a projected CRS')
is_first_field = True
if is_first_field:
    print('TEST MODE: Only processing first field file')
for f in os.listdir(field_aoi_dir):
    aoi_file = os.path.join(field_aoi_dir, f)
    # print('AOI File: {}'.format(aoi_file))
    if os.path.isfile(aoi_file) and f.endswith('AllFieldsMultipolygonAOI_GeoJSON2.geojson'):    
        # print(f)
        field_aoi = pju.extract_geometry_from_geojson_file(aoi_file)
        # print(field_aoi)
        if is_first_field:
            feature_ids = search_planet(item_types, field_aoi, 
                asset_type, planet_api_key, planet_base_url, img_start_date_string,
                img_end_date_string, clear_percent)
            # print('should only see this once')
            is_first_field = False

            print(feature_ids)

#%% DOWNLOAD IMAGERY
# loop through all field aoi polygon files in aoi dir
print('Be sure that AOI polygons are epsg:4326, NOT a projected CRS')
is_first_field = True
if is_first_file:
    print('TEST MODE: Only processing first field file')
for f in os.listdir(field_aoi_dir):
    aoi_file = os.path.join(field_aoi_dir, f)
    # print('AOI File: {}'.format(aoi_file))
    if os.path.isfile(aoi_file) and f.endswith('.geojson'):
        # print(f)
        field_aoi = pju.extract_geometry_from_geojson_file(aoi_file)
        # print(field_aoi)
        if is_first_field and False: # use clipped dl method to get clipped rasters, this gets whole scene
            download_planet_rasters(download_save_dir, item_types, field_aoi, 
                asset_type, planet_api_key, planet_base_url, img_start_date_string,
                img_end_date_string, clear_percent, really_download_images=True, 
                overwrite_existing=False)
            # print('should only see this once')
            is_first_field = False


#%% DEBUGGING ####
from planet_raster_downloader import get_combined_search_filter, get_date_filter, get_geom_filter, get_property_range_filter

startf = get_date_filter('lte', img_end_date_string)
endf = get_date_filter('gte', img_start_date_string)
geof = get_geom_filter(field_aoi)
cloudf = get_property_range_filter('cloud_cover', 'lte', clear_percent)
allf = [startf, endf, geof, cloudf]
combinedf = get_combined_search_filter(allf)

print(allf)

# %% Debugging activate
import requests
import planet_credentials as plc
import json
def p(data):
    print(json.dumps(data, indent=2))
# set up session object and authenticate

session = requests.Session()
asset_activation_url = 'https://api.planet.com/data/v1/assets/eyJpIjogIjIwMjIxMDIzXzE1MzAxNV8wMl8yNDlhIiwgImMiOiAiUFNTY2VuZSIsICJ0IjogIm9ydGhvX2FuYWx5dGljXzRiX3NyIiwgImN0IjogIml0ZW0tdHlwZSJ9/activate'
#authenticate session with user name and password, pass in an empty string for the password
planet_api_key = plc.get_planet_api_key()
session.auth = (planet_api_key, "")
res = session.get(asset_activation_url)

assets = res.json()
print('ASSETS PRINT')
p(assets)
print()
asset_status = assets["status"]
print(asset_status)


# %% ***TESTING RASTER CLIPPING AND DOWNLOADING MODULE***
# root dir holding field boundary polygons. will loop through this and pull
# planet rasters using these as AOI's
# field_aoi_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldAOIsForPlanetDownload'
field_aoi_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\CombinedAOIsForPlanet100kmMinDownload'
download_save_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3'
planet_base_url = "https://api.planet.com/data/v1"
item_types = ['PSScene']
item_type = item_types[0]
asset_type = 'ortho_analytic_4b_sr'
bundle_type = 'analytic_sr_udm2'
planet_api_key = plc.get_planet_api_key()
really_download_images = True
debug_flag = True
# search params to get list of feature ids to pass to clip and orders api for dl
img_start_date_string = "2022-06-08T00:00:00.000Z"
img_end_date_string = "2022-10-31T00:00:00.000Z"
clear_percent = 80 #% of area not impacted by cloud, haze, shadow, or snow

orders = []

is_first_field = True
if is_first_field:
    print('TEST MODE: Only processing first field file')
for f in os.listdir(field_aoi_dir):
    aoi_file = os.path.join(field_aoi_dir, f)
    # print('AOI File: {}'.format(aoi_file))
    # if os.path.isfile(aoi_file) and f.endswith('.geojson'):
    # using multipolygon to pull and clip all fields at once 
    # hopefully this will also let me not exceed the monthly dl quota
    if os.path.isfile(aoi_file) and f.endswith('AllFieldsMultipolygonAOI_GeoJSON2.geojson'):    
        # print(f)
        field_aoi = pju.extract_geometry_from_geojson_file(aoi_file)
        # print(field_aoi)
        if is_first_field:
            feature_ids = search_planet(item_types, field_aoi, 
                asset_type, planet_api_key, planet_base_url, img_start_date_string,
                img_end_date_string, clear_percent)
            # print('should only see this once')
            is_first_field = False

            # filter results to only include one image per day
            # feature_ids_one_per_day = pju.select_one_raster_per_day(feature_ids)

            if not really_download_images:
                    print('Flag not set to actually download images, testing only.')
                    print()
            else:
                print('Downloading {}'.format(feature_ids))
                
                order = asyncio.run(order_and_download_clipped_rasters(field_aoi, download_save_dir, 
                    item_type, bundle_type, feature_ids, planet_api_key, debug_flag))
                orders.append(order)


print('Downloading clipped rasters complete.')
print('File location: {}'.format(download_save_dir))

# loop through orders and get 
# orders[0]['_links']['_self'] in each then hit that and get
# order['_links']['results']
# and loop through that to get each result['location']

#%% 
# DOWNLOAD BY ORDER ID
# Call Planet's download method directly to see if this works:
# works - was issue with download url redirecting to new location
# hard coded url update in planet's orders.py file and dl now works
import os
from planet_raster_downloader import get_planet_download_stats, download_planet_rasters, search_planet
import planet_credentials as plc
import planet_json_utils as pju
from planet_raster_downloader_v2 import order_and_download_clipped_rasters, download_order
import asyncio
#fix issue with asyncio running in VSode ipython
import nest_asyncio
nest_asyncio.apply()

order_id = '071aa6dd-592b-4f36-9720-94dd11ecbf51'
download_save_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing'
planet_api_key = plc.get_planet_api_key()

files = download_order(order_id, download_save_dir, planet_api_key)
print('Downloaded:')
decoded_files = asyncio.gather(files)
print(decoded_files)


# %% testing method to get single image per day
test_ids = ['20220505_150056_52_2458', '20220422_150137_05_2455', 
            '20220422_150134_77_2455', '20220503_154639_90_227c', 
            '20220505_153231_29_2474', '20220505_153228_99_2474', 
            '20220429_155044_93_2413', '20220430_153257_14_2483', 
            '20220425_154730_22_2407', '20220425_154727_94_2407', 
            '20220424_154550_97_2424', '20220424_154553_28_2424', 
            '20220415_153036_53_2489', '20220413_153050_66_2479', 
            '20220413_153048_14_2479', '20220411_154350_40_241c', 
            '20220411_152843_1002']
single_day_ids = pju.select_one_raster_per_day(test_ids)
print(single_day_ids)
# %%
