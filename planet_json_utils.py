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
