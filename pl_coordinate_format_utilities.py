"""JUST EXPORT POLYGONS AS GEOJSON  FROM QGIS AND DON'T USE THIS
NOT FINISHED/NOT WORKING YET. SEE ABOVE.
"""

#%% library imports
import pandas as pd
import json

#%% functions
def convert_wkt_to_geojson_coord(coord):
    lCoordPairs = coord.split(',')
    sOut = ''
    lOut = []
    for c in lCoordPairs:
        lOut.append('[{}]'.format(c.replace(' ', ',')))

    sOut = ','.join(lOut)
    sOut = '[{}]'.format(sOut)
    return sOut

def convert_wkt_to_planet_geojson_object(input_file_path, wkt_coords_column_name, geometry_type):
    df = pd.read_csv(input_file_path)
    df = df.assign(Converted=lambda x: convert_wkt_to_geojson_coord(x[wkt_coords_column_name]))
    coords_list = df['Converted']
    print('Converted Coords List: {}'.format(coords_list))
    geom = {
        "type": geometry_type,
        "coordinates": [
          [
            # json.dumps(coords_list.to_list())
            coords_list.to_json()
          ]
        ]
    }

    return geom
#%% call the func to get the geom object used by Planet's geometry filter
coordsFilePath = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldPolygonCoords.csv'
coordsColName = 'PolygonCoords'
geometryType = 'Polygon'

geom = convert_wkt_to_planet_geojson_object(coordsFilePath, coordsColName, geometryType)

print(geom)

# %%DEBUGging
df = pd.read_csv(coordsFilePath)
#%%
wkt_coords_column_name = coordsColName
df = df.assign(Converted=lambda x: convert_wkt_to_geojson_coord(x[wkt_coords_column_name]))
coords_list = df['Converted']
print('Converted Coords List: {}'.format(coords_list))
# %%
