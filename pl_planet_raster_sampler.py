#%% Import libs
import os
import json
from random import sample
import geopandas as gp
import pandas as pd
import rasterio
from shapely.geometry import point

#%% Functions
def get_xy_from_gdf(gdf):
    return [(x,y) for x,y in zip(gdf['geometry'].x , gdf['geometry'].y)]

def sample_raster_by_points(raster_file_path, sample_points_gdf, bands_to_sample, crs='EPSG:4326'):
    # create output gdf containing our sample points
    gdfRet = sample_points_gdf[['Pixel_number', 'geometry']].copy()

    raster = rasterio.open(raster_file_path)
    # rasterio needs list of coords in x,y; use fxn to do this
    coord_list = get_xy_from_gdf(sample_points_gdf)

    # sample the raster using the points list and store them in a new column in output gdf   
    gdfRet['SampleValue'] = [x for x in raster.sample(coord_list)]

    # NOTE: returns gdf in form of [[Index, Geometrey (point), SampleValue[a,b,c,d]]]
    return gdfRet

def get_date_from_planet_raster_name(fname):
    # parse raster filename to extract acquisition date
    # filname in format of:
    # 20220918_154732_85_2414_3B_AnalyticMS_SR.tif
    # YYYYMMDD_HHMMSS_??_<satellite id>_<product level>_<product type>.tif
    raster_date = 'TODO'
    return raster_date

#%% Constants
RASTER_FILE_DIR = r'C:\Users\P\Pictures\PythonTestDownloads'
POINT_FILE_PATH = r'C:\Users\P\Pictures\PythonTestDownloads\PixelLocations_Approximate.csv'

OUTPUT_FILE_DIR = r'G:\My Drive\Cornell\DigitalAgGroup\Projects\Louis_Yuji_Planet\Output'
OUTPUT_CSV_NAME = r'PlanetSampleTest.csv'

# planet raster bands that we need to sample
SAMPLE_BAND_LIST = [1,2,3,4]

#%% Create gdf to hold sample value output from all rasters
gdf_sample_values = gp.GeoDataFrame(columns=['Id', 'PointId', 'RasterId', 'RasterDate', 'SampleValue', 'RasterFileName'])

#%% Load sample points data
sample_points_gdf = gp.read_file(POINT_FILE_PATH)

# create the geometry obj from  x and y coord cols present in the csv
pt_geos = gp.points_from_xy(sample_points_gdf['x'], sample_points_gdf['y'])
# add geometry point objs to the gdf
sample_points_gdf.geometry = pt_geos
sample_points_gdf.set_geometry(sample_points_gdf.geometry) 
#set default unprojected WGS84 crs
sample_points_gdf.crs = 'EPSG:4326'

#%% reproject points list to same crs as raster
# hard coded for now, change this to load the raster, pull the crs
# then use that to reproject the points to the same crs
if sample_points_gdf.crs != 'EPSG:32618':
    sample_points_gdf = sample_points_gdf.to_crs('EPSG:32618')

#%% 
# TODO: Convert to fxn once tested
# encode file path
# dir = os.fsencode(RASTER_FILE_DIR)

# set list of file extensions to process - DNW, using simpler approach
# file_exts_to_proc = ['.tif']
# # convert list to tuple
# file_exts_to_proc = tuple(file_exts_to_proc)

# Loop through rasters and sample values at sample point locations
for f in os.listdir(RASTER_FILE_DIR):
    if '.tif' in f and '.aux.xml' not in f: #
        # store descriptive data about raster file
        raster_name = f
        raster_date = get_date_from_planet_raster_name(f)
        # construct path to raster file
        raster_file_path = os.path.join(RASTER_FILE_DIR, f)

        # sample raster band values for all points
        print('PROCCESSING {}'.format(f))
        point_values_gdf = sample_raster_by_points(raster_file_path, sample_points_gdf, SAMPLE_BAND_LIST, 'EPSG:4326')
        
        # set file name that we are sampling
        point_values_gdf['RasterFileName'] = f
        # TODO: add additional cols to point_values_gdf to make cols match those of output gdf
        
        # append values to our output gdf
        gdf_sample_values = gp.GeoDataFrame(pd.concat(
                        [gdf_sample_values, point_values_gdf], ignore_index=True))
        gdf_sample_values.set_crs(point_values_gdf.crs)
        # or maybe this:
        # dataframesList = [gdf_sample_values, point_values_gdf]
        # gdf_sample_values = gp.GeoDataFrame( pd.concat( dataframesList, ignore_index=True),
        #   crs=dataframesList[0].crs )

        #return(gdf_sample_values)
out_path = os.path.join(OUTPUT_FILE_DIR, OUTPUT_CSV_NAME)
gdf_sample_values.to_csv(out_path)
print('PROCCESSING COMPLETE')

# %%
