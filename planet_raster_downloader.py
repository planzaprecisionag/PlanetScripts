#%%
# import api credentials from centralized credentials file
import planet_credentials as p_creds
# other lib imports
import os
import requests
import asyncio
import planet
import json
import geojsonio
import geopandas
import rasterio
import traceback

#%%init class
# class Planet_Raster_Downloader:
#     def __init__(self, PLANET_API_KEY):
#         SESSION = requests.Session()

#         #authenticate session with user name and password, pass in an empty string for the password
#         SESSION.auth = (PLANET_API_KEY, "")

#%% DEBUGGING
# use this var to get values from within fxns for ts'ing
debug_var = ''

#%% main code entrypoints
def get_planet_download_stats(download_save_dir:str, item_types:list, aoi_geojson_geom, 
    asset_type:str, planet_api_key:str, planet_base_url:str, img_start_date:str, 
    img_end_date:str, clear_percent, interval_type, *args, **kwargs):

    # set up session object and authenticate
    session = requests.Session()

    #authenticate session with user name and password, pass in an empty string for the password
    session.auth = (planet_api_key, "")

    # get individual filters
    geo_filter = get_geom_filter(aoi_geojson_geom)
    start_date_filter = get_date_filter('gte', img_start_date)
    end_date_filter = get_date_filter('lte', img_end_date)
    cloud_filter = get_property_range_filter('clear_percent', 'gte', clear_percent)
    # combine them into one 'and' filter
    filter_list = [geo_filter, start_date_filter, end_date_filter, cloud_filter]
    search_filter = get_combined_search_filter(filter_list)

    stats_url = "{}/stats".format(planet_base_url)
    item_types = item_types

    # Setup the request
    request = {
        "item_types" : item_types,
        "interval" : interval_type,
        "filter" : search_filter
    }

    # print(request)

    # Send the POST request to the API stats endpoint
    res=session.post(stats_url, json=request)

    # sanity check 
    # Print response
    p(res.json())


def download_planet_rasters(download_save_dir:str, item_types:str, aoi_geojson_geom, 
    asset_type:str, planet_api_key:str, planet_base_url:str, img_start_date:str, 
    img_end_date:str, clear_percent, really_download_images = False, 
    overwrite_existing = False, *args, **kwargs):

    # set up session object and authenticate
    session = requests.Session()

    #authenticate session with user name and password, pass in an empty string for the password
    session.auth = (planet_api_key, "")

    # get individual filters
    geo_filter = get_geom_filter(aoi_geojson_geom)
    start_date_filter = get_date_filter('gte', img_start_date)
    end_date_filter = get_date_filter('lte', img_end_date)
    cloud_filter = get_property_range_filter('clear_percent', 'gte', clear_percent)
    # combine them into one 'and' filter
    filter_list = [geo_filter, start_date_filter, end_date_filter, cloud_filter]
    search_filter = get_combined_search_filter(filter_list)

    quick_url = "{}/quick-search".format(planet_base_url)

    # make new request to the data api
    request = {
        "item_types" : item_types,
        "filter" : search_filter
    }

    fetch_page(quick_url, really_download_images, session, download_save_dir, planet_api_key, search_json=request, overwrite_existing=overwrite_existing)

    print('Processing Complete')

    return

#%% utility methods
def get_geom_filter(geom):
    geometry_filter = {
        "type": "GeometryFilter",
        "field_name": "geometry",
        "config": geom
    }

    return geometry_filter

"""
conditional_type examples: get, lte
date_string example: 2021-06-13T00:00:00.000Z
"""
def get_date_filter(conditional_type, date_string):
    date_filter = {
        "type": "DateRangeFilter", # Type of filter -> Date Range
        "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
        "config": {
            conditional_type: date_string, # "gte" -> Greater than or equal to
        }
    }

    return  date_filter

"""
ex: cloud_cover_filter = {
"type": "RangeFilter",
"field_name": "cloud_cover",
"config": {
    "lte": 0.6
}
}
"""
def get_property_range_filter(field_name, conditional_type, property_value):
    filter = {
        "type": "RangeFilter",
        "field_name": field_name,
        "config": {
            conditional_type: property_value
        }
    }

    return filter
    
def get_combined_search_filter(filter_list):
    filter = {
        "type": "AndFilter",
        "config": filter_list
    }

    return filter
#%% setup global vars   
# PLANET_API_KEY = p_creds.get_planet_api_key()
# BASE_URL = "https://api.planet.com/data/v1"
# save_dir = r'C:\Users\P\Pictures\PythonTestDownloads'

# %%
# Search for imagery from our test fields on Cornell's campus
# Setup GeoJSON 
# 
# TODO: read in geoJSON file (created via QGIS polygon export of AOI's) and loop through each
# field and pull down Planet rasters
# TODO: check to see if the  file DNE locally before downloading (via the file's name vs 
# Planet files already downloaded)
# geom = {
#     "type": "Polygon",
#         "coordinates": [
#           [
#             [
#               -76.460702419281,
#               42.450694723657
#             ],
#             [
#               -76.46080970764159,
#               42.44592889231982
#             ],
#             [
#               -76.45516633987427,
#               42.445723050904434
#             ],
#             [
#               -76.45465135574341,
#               42.45056806173387
#             ],
#             [
#               -76.460702419281,
#               42.450694723657
#             ]
#           ]
#         ]
# }

# # Setup Geometry Filter
# geometry_filter = {
#     "type": "GeometryFilter",
#     "field_name": "geometry",
#     "config": geom
# }

# # Setup Date Filter
# date_filter_start = {
#     "type": "DateRangeFilter", # Type of filter -> Date Range
#     "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
#     "config": {
#         "gte": "2021-06-13T00:00:00.000Z", # "gte" -> Greater than or equal to
#     }
# }
# date_filter_end = {
#     "type": "DateRangeFilter", # Type of filter -> Date Range
#     "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
#     "config": {
#         "lte": "2021-11-05T00:00:00.000Z", # "lte" -> less than or equal to
#     }
# }

# # filter any images which are more than nn% clouds
# cloud_cover_filter = {
#   "type": "RangeFilter",
#   "field_name": "cloud_cover",
#   "config": {
#     "lte": 0.6
#   }
# }

# # Setup an "AND" logical filter
# and_filter = {
#     "type": "AndFilter",
#     "config": [geometry_filter, date_filter_start, date_filter_end, cloud_cover_filter]
# }

# sanity check
# Print the logical filter
# p(and_filter)

#%% set up session
# session = requests.Session()

# #authenticate session with user name and password, pass in an empty string for the password
# session.auth = (PLANET_API_KEY, "")

# #make a get request to the Data API to verify if working
# res = session.get(BASE_URL)

# # print response (should be 200 if good)
# print(res.status_code)


# %% FUNC DEFS
# Helper function to printformatted JSON using the json module
def p(data):
    print(json.dumps(data, indent=2))

def call_dl_fxn(perform_download, location_url, save_dir, planet_api_key, filename=None, overwrite_existing=False):
    if perform_download:
        fName = pl_download(location_url, save_dir, planet_api_key, overwrite_existing=overwrite_existing)
        print (r'Download Complete: {}\{}'.format(save_dir, fName))
    else:
        print('Download not enabled. Change reallyDownloadTheImage to true to download')
        print('iterated over {}'.format(location_url))

# download file and save to fs
# TODO: refactor to use expoential retry activation fxn
def pl_download(url, savepath, planet_api_key, filename=None, overwrite_existing=False):
    # Send a GET request to the provided location url, using your API Key for authentication
    res = requests.get(url, stream=True, auth=(planet_api_key, ""))
    # If no filename argument is given
    if not filename:
        # Construct a filename from the API response
        if "content-disposition" in res.headers:
            filename = res.headers["content-disposition"].split("filename=")[-1].strip("'\"")
        # Construct a filename from the location url
        else:
            filename = url.split("=")[1][:10]
    # Save the file
    # with open('output/' + filename, "wb") as f:

    # check to see if file exists before downloading
    full_file_path = os.path.join(savepath, filename)
    if not os.path.exists(full_file_path) or overwrite_existing: 
        with open(full_file_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()

    return filename

"""
Exponential retry fxn (from planet code example at
https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/toar/toar_planetscope.ipynb

"""
def activate_asset(asset_activation_url, session):
    asset_activated = False

    while asset_activated == False:
        # Send a request to the item's assets url\
        res = session.get(asset_activation_url)

        # Assign a variable to the item's assets url response
        assets = res.json()
        print('ASSETS PRINT')
        p(assets)
        print()
        asset_status = assets["status"]
        print(asset_status)

        # If asset is already active, we are done
        if asset_status == 'active':
            asset_activated = True
            print("Asset is active and ready to download")

    # Print the asset data    
    # return p(asset)

# How to Paginate:
# 1) Request a page of search results
# 2) do something with the page of results
# 3) if there is more data, recurse and call this method on the next page.
# adapted from code from here:
# https://developers.planet.com/docs/planetschool/best-practices-for-working-with-large-aois/pagination.py
# What we want to do with each page of search results
# in this case, just print out each id
def handle_page(res, really_download_images, session, save_dir, planet_api_key, overwrite_existing=False):
    if isinstance(res, dict):
        json_response = res
    else:
        json_response = res.json()
    # debugging
    # print('JSON RESPONSE BELOW')
    # p(json_response)
    # end debugging
    features = json_response["features"]
    # Print the response
    # p(geojson)

    #store # of features returned
    feature_count = len(features)
    # Get the number of features present in the response
    print('Features present: {}'.format(feature_count))

    for f in features:
        # show cloud coverage %
        # print('Percent Cloud Coverage:')
        # p(f['properties']['cloud_percent'])
        # print('')
        # Get the assets link for the item
        assets_url = f["_links"]["assets"]
        
        # Send a GET request to the assets url for the item (Get the list of available assets for the item)
        res = session.get(assets_url)

        # Assign a variable to the response
        assets = res.json()

        # Debugging - see how xml radiance conversion coeff files are named
        # print()
        # print('Assets JSON:')
        # p(assets)
        # print()
        
        #rad. calibrated img to surface reflectance
        # 4 band, ortho rectified, corrected to BOA reflectance
        # visual = assets["analytic_sr"] 
        # 8 band, ortho rectified, corrected to BOA reflectance
        # visual = assets["ortho_analytic_8b_sr"] 
        # 4-band radiometrically calibrated, TOA
        try:
            # visual = assets["analytic_sr"]
            # visual_xml = assets["analytic_sr_xml"]
            # orthoanalytic_asset_4b = assets["ortho_analytic_4b"]
            # orthoanalytic_xml_asset_4b = assets["ortho_analytic_4b_xml"]
            orthoanalytic_asset_4b_sr = assets["ortho_analytic_4b_sr"]
            # DONT NEED XML for SR because already REFLECTANCE
            # orthoanalytic_xml_asset_4b_sr = assets["ortho_analytic_4b_sr_xml"]
            # orthoanalytic_asset_8b = assets["ortho_analytic_8b"]
            # orthoanalytic_xml_asset_8b = assets["ortho_analytic_8b_xml"] 

            # Setup the activation url for a particular asset (in this case the visual asset)
            # activation_url_visual = visual["_links"]["activate"]
            # activation_url_visual_xml = visual_xml["_links"]["activate"]
            # activation_url_orthoanalytic_asset_4b = orthoanalytic_asset_4b["_links"]["activate"]
            # activation_url_orthoanalytic_xml_asset_4b = orthoanalytic_xml_asset_4b["_links"]["activate"]
            activation_url_orthoanalytic_asset_4b_sr = orthoanalytic_asset_4b_sr["_links"]["activate"]
            # activation_url_orthoanalytic_asset_8b = orthoanalytic_asset_8b["_links"]["activate"]
            # activation_url_orthoanalytic_xml_asset_8b = orthoanalytic_xml_asset_8b["_links"]["activate"]
            
            # Send a request to the activation url to activate the item and
            # its radiance to reflectance conversion coefficients xml file
            print('Attempting to activate: {}'.format(activation_url_orthoanalytic_asset_4b_sr))
            res = session.get(activation_url_orthoanalytic_asset_4b_sr)
            # res_xml = session.get(activation_url_orthoanalytic_asset_4b_sr)
            # TODO: Implement dl for 8band and XML files

            # Print the response from the activation request
            print()
            print('Activation Result Code:')
            p(res.status_code) # 204 if ready   
            print()     

            #TODO write exponential retry code to attempt to dl images that aren't ready
            
            if res.status_code == 204:
                # ** DOWNLOAD ONCE ASSET IS ACTIVE (RESPONSE CODE 204)
                # Assign a variable to the visual asset's location endpoint
                location_url = orthoanalytic_asset_4b_sr["location"]
                # print('Location URL: {}'.format(location_url))
                # location_url_xml = orthoanalytic_xml_asset_8b["location"]

                # TODO: alter url to specify that images should be sent to google cloud
                # storage assets folder using code from 
                # here: https://developers.planet.com/docs/integrations/gee/delivery/#example-gee-delivery-payloads
                # and here: https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/orders/ordering_and_delivery.ipynb

                # Download the file from an activated asset's location url IF we are actually downloading
                call_dl_fxn(really_download_images, location_url, save_dir, planet_api_key, filename=None, overwrite_existing=overwrite_existing)
                # call_dl_fxn(reallyDownloadTheImage, location_url_xml, save_dir, filename=None)
            elif res.status_code == 202:
                # exponential wait retry to get the image ready to download  from Planet
                # NOTE: currently, this code does exponential wait retry one-by-one, blocking 
                # subsequent downloads until image is ready and downloaded;
                # may need to refactor this to allow continued/paralled dl calls while waiting
                # for image activation if this causes delays
                activate_asset(activation_url_orthoanalytic_asset_4b_sr, session)
                # activate_asset(assets_url, orthoanalytic_xml_asset_8b)
                # Download the file from an activated asset's location url if flag set to do
                # otherwise, show msg saying not dl'd and show image name

                # NOTE: lcoation key node not present until asset ready for dl, so must get it here
                # once asset activation is complete
                location_url = activation_url_orthoanalytic_asset_4b_sr["location"]
                # location_url_xml = orthoanalytic_xml_asset_8b["location"]

                # with all of that done, we can now dl the image and xml coeff file
                # (if we are actually downloading and not just testing / iterating through the assets)
                call_dl_fxn(really_download_images, location_url, save_dir, planet_api_key, filename=None, overwrite_existing=overwrite_existing)
                # call_dl_fxn(reallyDownloadTheImage, location_url_xml, save_dir, filename=None)
            else:
                next
        except Exception as e:
            print('Error downloading (or activating){}'.format(f['_links']))
            traceback.print_exc()
            print('EXCEPTION: {}'.format(repr(e)))            
        next
    print('Processing (downloads) complete (for this page of results). Moving to next page of results (if present)')
    return 

def fetch_page(search_url, really_download_images, session, save_dir, planet_api_key, search_json = '', overwrite_existing=False):
    print('Processing results from {}'.format(search_url))
    if search_json != '':
        p(search_json)
        # NOTE: MUST do json=... to avoid missing post body error msg when posting like below
        res = session.post(search_url, json=search_json)
    else:
        print('PROCCESSING NEXT PAGE. Search params carried over from initial  search')
        res = session.get(search_url).json()

        #debugging:
        debug_var = res
    # sanity check 
    # Print response
    # p(res.json())

    handle_page(res, really_download_images, session, save_dir, planet_api_key, overwrite_existing=overwrite_existing)

    # fixing TypeError: 'Response' object is not subscriptable on next pages
    try:
        next_url = res["_links"].get("_next")
    except:
        resJSON = res.json()
        next_url = resJSON["_links"].get("_next")

        traceback.print_exc()

    if next_url:
        fetch_page(next_url, really_download_images, session, save_dir, planet_api_key, overwrite_existing=overwrite_existing) 
    
    print('Finished processing results from {}'.format(search_url))

#%% Setting up the API request

# The /stats endpoint provides a summary of the available data based on some search criteria.
# https://api.planet.com/data/v1/stats
# Setup the stats URL
# stats_url = "{}/stats".format(BASE_URL)

# #specify item types to pull
# # PSScene4Band and PSScene documentation links:
# # https://developers.planet.com/docs/data/psscene4band/
# # https://developers.planet.com/docs/data/psscene/
# # item_types = ["PSScene4Band", "PSScene"] #maybe also include to PSScene (which is up to 8band)
# item_types = ["PSScene"]
# # item_types = ["PSScene"]
# # TODO: verify that PSScene4Band is coming from AnalyticSR or analytic_8b_sr_udm2
# #  bundle (calibrated, BOA), should be, but verify this

# # Setup the request
# request = {
#     "item_types" : item_types,
#     "interval" : "year",
#     "filter" : and_filter
# }

# # Send the POST request to the API stats endpoint
# #res=session.post(stats_url, json=request)

# # sanity check 
# # Print response
# p(res.json())

#%%
# Setup the quick search endpoint url to search for imagery meeting xyz criteria
# quick_url = "{}/quick-search".format(BASE_URL)

# # make new request to the data api
# request = {
#     "item_types" : item_types,
#     "filter" : and_filter
# }

#%% new process flow - get page then pass to fetch_page to allow for pagination
# fetch_page(quick_url, search_json=request)

# print('Processing Complete')

