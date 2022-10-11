# Examples from 
# https://developers.planet.com/docs/apis/data/api-mechanics/
# also: https://notebook.community/planetlabs/notebooks/jupyter-notebooks/data-api-tutorials/planet_data_api_introduction


#%%
# import api credentials from centralized credentials file
import planet_credentials as p_creds

#%% Authentication via basic HTTP example
import os
# import os module to access enviornmental modules

import requests
import asyncio
import os
import planet
import requests
import json
import geojsonio

# %%
# Helper function to printformatted JSON using the json module
def p(data):
    print(json.dumps(data, indent=2))

os.environ['PLANET_API_KEY']= p_creds.get_planet_api_key()
# pass in your API key

PLANET_API_KEY = os.getenv('PLANET_API_KEY')
# Setup the API Key from the `PL_API_KEY` environment variable

BASE_URL = "https://api.planet.com/data/v1"

session = requests.Session()
#setup a session

session.auth = (PLANET_API_KEY, "")
#authenticate session with user name and password, pass in an empty string for the password

res = session.get(BASE_URL)
#make a get request to the Data API

print(res.status_code)
# test response

print(res.text)
# print response body

#%%
# The /stats endpoint provides a summary of the available data based on some search criteria.
# https://api.planet.com/data/v1/stats
# Setup the stats URL
stats_url = "{}/stats".format(BASE_URL)

# Print the stats URL
print(stats_url)

# %%
# Specify the sensors/satellites or "item types" to include in our results
item_types = ["PSScene4Band", "REOrthoTile"]

# Create filter object for all imagery captured between 2013-01-01 and present.
date_filter = {
    "type": "DateRangeFilter", # Type of filter -> Date Range
    "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
    "config": {
        "gte": "2021-01-01T00:00:00.000Z", # "gte" -> Greater than or equal to
    }
}

# %%
# Construct the request.
request = {
    "item_types" : item_types,
    "interval" : "year",
    "filter" : date_filter
}

# Send the POST request to the API stats endpoint
res = session.post(stats_url, json=request)

# Print response
p(res.json())

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

# %% Setup instrument type filter
# Setup Item Types
# item_types = ["PSScene4Band"]

# # Setup Instrument Filter
# instrument_filter = {
#     "type": "StringInFilter",
#     "field_name": "instrument",
#     "config": ["PS2"]
# }

# # Setup "not" Logical Filter
# not_filter = {
#     "type": "NotFilter",
#     "config": instrument_filter
# }

# # Setup the request
# request = {
#     "item_types" : item_types,
#     "interval" : "year",
#     "filter" : not_filter
# }

#%% Combine the date range and geometry filters using an AND FILTER
# Setup an "AND" logical filter
and_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_filter]
}

# Print the logical filter
p(and_filter)

#%%
# Setup the request
request = {
    "item_types" : item_types,
    "interval" : "year",
    "filter" : and_filter
}

# Send the POST request to the API stats endpoint
res=session.post(stats_url, json=request)

# Print response
p(res.json())

# %% *********** QUICK SEARCH *************
# Setup the quick search endpoint url
quick_url = "{}/quick-search".format(BASE_URL)

#%%
# Setup Item Types
item_types = ["PSScene4Band"]

# Setup GeoJSON for only imagery that intersects with 40N, 90W
# geom = {
#     "type": "Point",
#     "coordinates": [
#         -90,
#          40
#     ]
# }

# Setup a geometry filter
geometry_filter = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": geom
}

# Setup the request
request = {
    "item_types" : item_types,
    "filter" : geometry_filter
}

#%%
p(request)

# Send the POST request to the API quick search endpoint
res = session.post(quick_url, json=request)

# Assign the response to a variable
geojson = res.json()

# Print the response
p(geojson)

# %%
# Assign a features variable 
features = geojson["features"]

# Get the number of features present in the response
len(features)

# %%
# Loop over all the features from the response
for f in features:
    # Print the ID for each feature
    p(f["id"])

# %% *** PAGING RESULTS > 250 ***
# Print the response "_links" property
p(geojson["_links"])

# %%
# Assign the "_links" -> "_next" property (link to next page of results) to a variable 
next_url = geojson["_links"]["_next"]

# Print the link to the next page of results
print(next_url)

#%% *** SETTING PAGE SIZE ***
# Send the POST request to the API quick search endpoint with a page size of 5
res = session.post(quick_url, json=request, params={"_page_size" : 5})

# Assign the response to a variable
geojson = res.json()

# Get the number of features present in the response
len(geojson["features"])

# %% use GEOJSONIO to displaly area footprints
# Assign the url variable to display the geojsonio map
url = geojsonio.display(res.text)

#%% Iterate through pages
# Assign the next_url variable to the next page of results from the response (Setup the next page of results)
next_url = geojson["_links"]["_next"]

# Get the next page of results
res = session.get(next_url)

# Assign the response to a variable
geojson = res.json()

# Get the url see results on geojson.io
url = geojsonio.to_geojsonio(res.text)

#%%
# Setup the next page of results
next_url = geojson["_links"]["_next"]

# Get the next page of results
res = session.get(next_url)

# Assign the response to a variable
geojson = res.json()

# Get the url see results on geojson.io
url = geojsonio.to_geojsonio(res.text)

# %% *** FEATURES AND PERMISSIONS ***
# Assign a variable to the search result features (items)
features = geojson["features"]

# Get the first result's feature
feature = features[0]

# Print the ID
p(feature["id"])

# Print the permissions
p(feature["_permissions"])

#%%
# Get the assets link for the item
assets_url = feature["_links"]["assets"]

# Print the assets link
print(assets_url)

# %%
# Send a GET request to the assets url for the item (Get the list of available assets for the item)
res = session.get(assets_url)

# Assign a variable to the response
assets = res.json()
# Print the asset types that are available
print(assets.keys())

#%%
# Assign a variable to the visual asset from the item's assets
visual = assets["analytic"]

visual = assets["analytic_sr"] #rad. calibrated img to surface reflectance

# Print the visual asset data
p(visual)

#%% print all feature json so I can see what I can dl
# p(feature)

#%%
# print feature's  cloud cover %
p(feature["properties"]["cloud_percent"])

# %%
# Setup the activation url for a particular asset (in this case the visual asset)
activation_url = visual["_links"]["activate"]

# Send a request to the activation url to activate the item
res = session.get(activation_url)

# Print the response from the activation request
p(res.status_code)

# %%
# ** DOWNLOAD ONCE ASSET IS ACTIVE (RESPONSE CODE 204)
# Assign a variable to the visual asset's location endpoint
location_url = visual["location"]

# Print the location endpoint
print(location_url)

#%%
# Create a function to download asset files
# Parameters: 
# - url (the location url)
# - filename (the filename to save it as. defaults to whatever the file is called originally)

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

# %%
# Download the file from an activated asset's location url
save_dir = r'C:\Users\P\Pictures\PythonTestDownloads'
fName = pl_download(location_url, save_dir)
print ('Download Complete: {}'.format(fName))

# %%
