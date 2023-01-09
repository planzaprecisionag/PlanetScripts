#%% lib imports
import json

#%% extract geometry attribute from geojson (exported from QGIS) for Planet API 
# AOI filter
def extract_geometry_from_geojson_file(file_path):
    # open file
    f = open(file_path)

    # load geojson into dict
    geojson = json.load(f)

    # extract value from geometry key
    features = geojson['features']
    geom = features[0]['geometry']

    return geom

#%% testing - delete when done
# file_path = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldAOIsForPlanetDownload\Field1PolygonCoords_GeoJSON_epsg32618.geojson'
# # open file
# f = open(file_path)

# # load geojson into dict
# geojson = json.load(f)
# # print(geojson.keys())

# # extract value from geometry key
# features = geojson['features']
# # NOTE: the features element is a single-element list of dicts
# geom = features[0]['geometry']
# print(geom)
# # %%
def p(data):
    print(json.dumps(data, indent=2))

# code from: https://stackoverflow.com/questions/2170900/get-first-list-index-containing-sub-string
def first_substring(strings, substring):
    return next(i for i, string in enumerate(strings) if substring in string)

# returns first image taken on a given day
# this is done to address an issue with there being two
# rasters for a given aoi taken a few seconds apart sometimes
def select_one_raster_per_day(asset_ids):
    index_list = []
    for id in asset_ids:
        day = id.split('_')[0]
        # print(day)
        index = first_substring(asset_ids, day)
        # print(index)
        # print(test_ids[index])
        # print()
        if not index in index_list:
            index_list.append(index)

    single_day_ids = [asset_ids[i] for i in index_list]

    return single_day_ids