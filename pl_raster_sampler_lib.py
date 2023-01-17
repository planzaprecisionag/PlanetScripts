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
    raster_time = fname.split('_')[1]
    return raster_time

def get_time_from_planet_raster_name(fname):
    # parse raster filename to extract acquisition date
    # filname in format of:
    # 20220918_154732_85_2414_3B_AnalyticMS_SR.tif
    # YYYYMMDD_HHMMSS_??_<satellite id>_<product level>_<product type>.tif
    raster_date = fname.split('_')[0]
    return raster_date


