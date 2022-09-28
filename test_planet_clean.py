#%%
# import api credentials from centralized credentials file
import planet_credentials as p_creds
# other lib imports
import os
import requests
import asyncio
import os
import planet
import requests
import json
import geojsonio

# %% FUNC DEFS
# Helper function to printformatted JSON using the json module
def p(data):
    print(json.dumps(data, indent=2))

# download file and save to fs
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
              -76.45966172218321,
              42.44760726631182
            ],
            [
              -76.45674347877502,
              42.44760726631182
            ],
            [
              -76.45674347877502,
              42.44900851581353
            ],
            [
              -76.45966172218321,
              42.44900851581353
            ],
            [
              -76.45966172218321,
              42.44760726631182
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
date_filter = {
    "type": "DateRangeFilter", # Type of filter -> Date Range
    "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
    "config": {
        "gte": "2021-08-01T00:00:00.000Z", # "gte" -> Greater than or equal to
    }
}

# filter any images which are more than 20% clouds
cloud_cover_filter = {
  "type": "RangeFilter",
  "field_name": "cloud_cover",
  "config": {
    "lte": 0.2
  }
}

# Setup an "AND" logical filter
and_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_filter, cloud_cover_filter]
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
item_types = ["PSScene4Band"]

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
for f in features[:1]:
    # show cloud coverage %
    print('Percent Cloud Coverage:')
    p(f['properties']['cloud_percent'])
    print('')

    # TODO: add code to only pull images having less than n% cloud cover as initial filter

    # Get the assets link for the item
    assets_url = f["_links"]["assets"]
    
    # Send a GET request to the assets url for the item (Get the list of available assets for the item)
    res = session.get(assets_url)

    # Assign a variable to the response
    assets = res.json()

    #rad. calibrated img to surface reflectance
    visual = assets["analytic_sr"] 

    # Setup the activation url for a particular asset (in this case the visual asset)
    activation_url = visual["_links"]["activate"]

    # Send a request to the activation url to activate the item
    res = session.get(activation_url)

    # Print the response from the activation request
    p(res.status_code) # 204 if ready

    #TODO write exponential retry code to attempt to dl images that aren't ready
    if res.status_code == 204:
        # ** DOWNLOAD ONCE ASSET IS ACTIVE (RESPONSE CODE 204)
        # Assign a variable to the visual asset's location endpoint
        location_url = visual["location"]

        # Download the file from an activated asset's location url
        save_dir = r'C:\Users\P\Pictures\PythonTestDownloads'
        fName = pl_download(location_url, save_dir)
        print (r'Download Complete: {}\{}'.format(save_dir, fName))
    else:
        # TODO: exponential retry
        next

# %%
