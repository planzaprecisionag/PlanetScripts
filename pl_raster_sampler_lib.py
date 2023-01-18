#%% Import libs
import os
import json
from random import sample
import geopandas as gp
import pandas as pd
import rasterio
from shapely.geometry import point
import warnings
warnings.filterwarnings(action='once')

#%% Functions
def get_xy_from_gdf(gdf):
    return [(x,y) for x,y in zip(gdf['geometry'].x , gdf['geometry'].y)]

def sample_raster_by_points_crop_height(raster_file_path, sample_points_gdf, bands_to_sample, crs='EPSG:4326'):
    # create output gdf containing our sample points
    gdfRet = sample_points_gdf[['Pixel_number', 'geometry']].copy()

    raster = rasterio.open(raster_file_path)
    # rasterio needs list of coords in x,y; use fxn to do this
    coord_list = get_xy_from_gdf(sample_points_gdf)

    # sample the raster using the points list and store them in a new column in output gdf   
    gdfRet['SampleValue'] = [x for x in raster.sample(coord_list)]

    # NOTE: returns gdf in form of [[Index, Geometrey (point), SampleValue[a,b,c,d]]]
    return gdfRet

def sample_rasters_by_points(raster_file_paths:dict, sample_points_gdf, bands_to_sample):
    # sample list of rasters by points
    gdf_ret = sample_points_gdf.copy()
    for key in raster_file_paths:
        with rasterio.open(raster_file_paths[key]) as raster:
            # rasterio needs list of coords in x,y; use fxn to do this
            coord_list = get_xy_from_gdf(sample_points_gdf)
            gdf_ret[key] = [x for x in raster.sample(coord_list, bands_to_sample)]

    # defragment the df by returning a copy
    return gdf_ret.copy()

def sample_rasters_by_points_planet_ofe_biological(raster_file_paths_by_farm:dict, sample_points_gdf, bands_to_sample, group_by_col_name):
    
    gdf_all_samples = gp.GeoDataFrame()
    grouped = sample_points_gdf.groupby(group_by_col_name)
    for key in raster_file_paths_by_farm:
        print('Sampling rasters for {}'.format(key))
        farm_gdf = None        
        # get gdf of points for current farm
        entity_gdf = grouped.get_group(key)
        # get rasters for current farm. is in form of {filename, full filepath}
        raster_dict = raster_file_paths_by_farm[key]
        # call sampler fxn to sample rasters for the current farm by its points
        if gdf_all_samples.empty == True:
            gdf_all_samples = sample_rasters_by_points(raster_dict, entity_gdf, bands_to_sample)
        else:
            # concat new sample data using pandas then convert back to gdf having same
            # crs as sample points data
            farm_gdf = sample_rasters_by_points(raster_dict, entity_gdf, bands_to_sample)
            gdf_all_samples = gp.GeoDataFrame(
                pd.concat([gdf_all_samples, farm_gdf], ignore_index=True), crs=sample_points_gdf.crs
            )
        print()
    print()
    print('Sampling Complete')
    print()
    return gdf_all_samples
    
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


