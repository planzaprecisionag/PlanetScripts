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


# %% FUNC DEFS
# Helper function to printformatted JSON using the json module
def p(data):
    print(json.dumps(data, indent=2))

def call_dl_fxn(perform_download, location_url, save_dir, filename=None):
    if perform_download:
        fName = pl_download(location_url, save_dir)
        print (r'Download Complete: {}\{}'.format(save_dir, fName))
    else:
        print('Download not enabled. Change reallyDownloadTheImage to true to download')
        print('iterated over {}'.format(location_url))

# download file and save to fs
# TODO: refactor to use expoential retry activation fxn
def pl_download(url, savepath, filename=None):
    
    # Send a GET request to the provided location url, using your API Key for authentication
    res = requests.get(url, stream=True, auth=(PLANET_API_KEY, ""))
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
    with open(os.path.join(savepath, filename), "wb") as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()

    return filename

"""
Exponential retry fxn (from planet code example at
https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/toar/toar_planetscope.ipynb

"""
def activate_asset(assets_url, asset):
    asset_activated = False

    while asset_activated == False:
        # Send a request to the item's assets url
        res = session.get(assets_url)

        # Assign a variable to the item's assets url response
        assets = res.json()

        asset_status = asset["status"]
        print(asset_status)

        # If asset is already active, we are done
        if asset_status == 'active':
            asset_activated = True
            print("Asset is active and ready to download")

    # Print the ps3b_analytic asset data    
    return p(asset)

#%% setup global vars   
PLANET_API_KEY = p_creds.get_planet_api_key()
BASE_URL = "https://api.planet.com/data/v1"

# %%
# Search for imagery from our test fields on Cornell's campus
# Setup GeoJSON 
geom = {
    "type": "Polygon",
        "coordinates": [
          [
            [
              -76.460702419281,
              42.450694723657
            ],
            [
              -76.46080970764159,
              42.44592889231982
            ],
            [
              -76.45516633987427,
              42.445723050904434
            ],
            [
              -76.45465135574341,
              42.45056806173387
            ],
            [
              -76.460702419281,
              42.450694723657
            ]
          ]
        ]
}

# Setup Geometry Filter
geometry_filter = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": geom
}

# Setup Date Filter
date_filter_start = {
    "type": "DateRangeFilter", # Type of filter -> Date Range
    "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
    "config": {
        "gte": "2021-06-13T00:00:00.000Z", # "gte" -> Greater than or equal to
    }
}
date_filter_end = {
    "type": "DateRangeFilter", # Type of filter -> Date Range
    "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
    "config": {
        "lte": "2021-11-05T00:00:00.000Z", # "lte" -> less than or equal to
    }
}

# filter any images which are more than nn% clouds
cloud_cover_filter = {
  "type": "RangeFilter",
  "field_name": "cloud_cover",
  "config": {
    "lte": 0.6
  }
}

# Setup an "AND" logical filter
and_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_filter_start, date_filter_end, cloud_cover_filter]
}

# sanity check
# Print the logical filter
# p(and_filter)

#%% set up session
session = requests.Session()

#authenticate session with user name and password, pass in an empty string for the password
session.auth = (PLANET_API_KEY, "")

#make a get request to the Data API to verify if working
res = session.get(BASE_URL)

# print response (should be 200 if good)
print(res.status_code)

#%% Setting up the API request

# The /stats endpoint provides a summary of the available data based on some search criteria.
# https://api.planet.com/data/v1/stats
# Setup the stats URL
stats_url = "{}/stats".format(BASE_URL)

#specify item types to pull
# PSScene4Band and PSScene documentation links:
# https://developers.planet.com/docs/data/psscene4band/
# https://developers.planet.com/docs/data/psscene/
item_types = ["PSScene4Band", "PSScene"] #maybe also include to PSScene (which is up to 8band)
# item_types = ["PSScene"]
# TODO: verify that PSScene4Band is coming from AnalyticSR or analytic_8b_sr_udm2
#  bundle (calibrated, BOA), should be, but verify this

# Setup the request
request = {
    "item_types" : item_types,
    "interval" : "year",
    "filter" : and_filter
}

# Send the POST request to the API stats endpoint
#res=session.post(stats_url, json=request)

# sanity check 
# Print response
p(res.json())

#%%
# Setup the quick search endpoint url to search for imagery meeting xyz criteria
quick_url = "{}/quick-search".format(BASE_URL)

# make new request to the data api
request = {
    "item_types" : item_types,
    "filter" : and_filter
}
# Send the POST request to the API quick search endpoint
res = session.post(quick_url, json=request)
# sanity check 
# Print response
p(res.json())

#%%
# Assign the response to a variable
geojson = res.json()
features = geojson["features"]
# Print the response
# p(geojson)

#store # of features returned
feature_count = len(features)
# Get the number of features present in the response
print('Features present: {}'.format(feature_count))

#%% Use geojson.io to show footprints of returned rasters
# probably a lot, can use paging to limit # returned per hit, then iterate through
# pages to limit number if many results returned
# TODO: TS why getting 401 auth error here and not in test code
# url = geojsonio.display(res.text)

#%% iterate through features and do things
# print feature's  cloud cover %
# note: do only first img for now
# get assets.ortho_analytic_8b_sr:download if available, otherwise 
# "assets.ortho_analytic_4b_sr:download
# for f in features[:1]:
for f in features:
    # show cloud coverage %
    # print('Percent Cloud Coverage:')
    # p(f['properties']['cloud_percent'])
    # print('')

    save_dir = r'C:\Users\P\Pictures\PythonTestDownloads'

    # Get the assets link for the item
    assets_url = f["_links"]["assets"]
    
    # Send a GET request to the assets url for the item (Get the list of available assets for the item)
    res = session.get(assets_url)

    # Assign a variable to the response
    assets = res.json()

    # Debugging - see how xml radiance conversion coeff files are named
    p(assets)
    
    #rad. calibrated img to surface reflectance
    # 4 band, ortho rectified, corrected to BOA reflectance
    # visual = assets["analytic_sr"] 
    # 8 band, ortho rectified, corrected to BOA reflectance
    # visual = assets["ortho_analytic_8b_sr"] 
    # 4-band radiometrically calibrated, TOA
    try:
        visual = assets["analytic_sr"]
        visual_xml = assets["analytic_sr_xml"]
        orthoanalytic_asset = assets["ortho_analytic_4b"]
        orthoanalytic_xml_asset = assets["ortho_analytic_4b_xml"]
        orthoanalytic_asset_8b = assets["ortho_analytic_8b"]
        orthoanalytic_xml_asset_8b = assets["ortho_analytic_8b_xml"] 

        # Setup the activation url for a particular asset (in this case the visual asset)
        activation_url_visual = visual["_links"]["activate"]
        activation_url_visual_xml = visual_xml["_links"]["activate"]
        activation_url_visual = orthoanalytic_asset["_links"]["activate"]
        activation_url_visual = orthoanalytic_xml_asset["_links"]["activate"]
        activation_url_visual = orthoanalytic_asset_8b["_links"]["activate"]
        activation_url_visual = orthoanalytic_xml_asset_8b["_links"]["activate"]
        
        # Send a request to the activation url to activate the item
        res = session.get(activation_url_visual)
        # TODO: Implement dl for 8band and XML files

        # Print the response from the activation request
        p(res.status_code) # 204 if ready        

        #TODO write exponential retry code to attempt to dl images that aren't ready
        reallyDownloadTheImage = False
        if res.status_code == 204:
            # ** DOWNLOAD ONCE ASSET IS ACTIVE (RESPONSE CODE 204)
            # Assign a variable to the visual asset's location endpoint
            location_url = visual["location"]

            # TODO: alter url to specify that images should be sent to google cloud
            # storage assets folder using code from 
            # here: https://developers.planet.com/docs/integrations/gee/delivery/#example-gee-delivery-payloads
            # and here: https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/orders/ordering_and_delivery.ipynb

            # Download the file from an activated asset's location url if flag set to do
            # otherwise, show msg saying not dl'd and show image name
            call_dl_fxn(reallyDownloadTheImage, location_url, save_dir, filename=None)
        elif res.status_code == 202:
            # exponential wait retry to get the image ready to download  from Planet
            # NOTE: currently, this code does exponential wait retry one-by-one, blocking 
            # subsequent downloads until image is ready and downloaded;
            # may need to refactor this to allow continued/paralled dl calls while waiting
            # for image activation if this causes delays
            activate_asset(assets_url, visual)

            # Download the file from an activated asset's location url if flag set to do
            # otherwise, show msg saying not dl'd and show image name
            call_dl_fxn(reallyDownloadTheImage, location_url, save_dir, filename=None)
        else:
            next
    except Exception as e:
      print('Error downloading (or activating){}'.format(f['_links']))
      print('EXCEPTION: {}'.format(e))
      next
print('Processing Complete - Do you need to implement paging?')


# %%