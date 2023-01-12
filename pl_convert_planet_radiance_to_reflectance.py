# convert planet raster values from radiance (W * m^-2 * sr ^-1) values 
# to reflectance (unitless,  0 to 1) values
# this is necessary to compare  imagery (i.e. timeseries analysis,  etc)
# code adapted from source at:
# https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/toar/toar_planetscope.ipynb

#%%
# Import helper modules
import json
import os
import rasterio
import numpy as np
from xml.dom import minidom

#%% FUNCTIONS
# Helper function to print formatted JSON using the json module
def p(data):
    print(json.dumps(data, indent=2))

def get_conversion_coeffs(asset_type, xml_coefficients_file_path):
    # read xml  file to extract band conversion coeffs
    xml_path = xml_coefficients_file_path
    xmldoc = minidom.parse(xml_path)
    nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")
    # XML parser refers to bands by numbers 1-4
    coeffs = {}
    for node in nodes:
        bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
        if '8b' not in asset_type:
            if bn in ['1', '2', '3', '4']:
                i = int(bn)
                value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
                coeffs[i] = float(value)
        else:
            if bn in ['1', '2', '3', '4', '5', '6', '7', '8']:
                i = int(bn)
                value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
                coeffs[i] = float(value)

    print("Conversion coefficients: {}".format(coeffs))
    return coeffs

def get_updated_fname(original_file_path):
    refl_fname = original_file_path.replace('.tif', '_refl.tif')
    return refl_fname

def do_conversion(asset_type, raster_file_path, coeffs):
    # update filename to show that is now holds reflectance values instead of radiance values
    refl_fname = get_updated_fname(raster_file_path)

    # scaling factor
    # this warrants some explanation: Reflectance is generally defined as a floating point number 
    # between 0 and 1, but image file formats are much more commonly stored as unsigned integers. 
    # A common practice in the industry is to multiply the radiance value by 10,000, 
    # then save the result as a file with data type uint16.
    scale = 10000

    # read raster file bands into np arrays
    if '8b' not in asset_type: # 4-band image, always same order
        # Load band data - note all PlanetScope 4-band images have band order BGRNIR
        with rasterio.open(raster_file_path) as src:
            band_blue_radiance = src.read(1)            
        with rasterio.open(raster_file_path) as src:
            band_green_radiance = src.read(2)
        with rasterio.open(raster_file_path) as src:
            band_red_radiance = src.read(3)
        with rasterio.open(raster_file_path) as src:
            band_nir_radiance = src.read(4)

        # Multiply the Digital Number (DN) values in each band by the TOA reflectance coefficients
        band_blue_reflectance = band_blue_radiance * coeffs[1]
        band_green_reflectance = band_green_radiance * coeffs[2]
        band_red_reflectance = band_red_radiance * coeffs[3]
        band_nir_reflectance = band_nir_radiance * coeffs[4]

        # Write out the new raster having reflectance instead of radiance values
        # Set spatial characteristics of the output object to mirror the input
        kwargs = src.meta
        kwargs.update(dtype=rasterio.uint16, count = 4)

        # Scale values. See note next to scale definition at top of this fxn for more info.
        # This is apparently common practice.
        blue_ref_scaled = scale * band_blue_reflectance
        green_ref_scaled = scale * band_green_reflectance
        red_ref_scaled = scale * band_red_reflectance
        nir_ref_scaled = scale * band_nir_reflectance

        # Write band calculations to a new raster file
        # NOTE: scaled to refl value [0-1] * 10000 to save as uint16
        with rasterio.open(refl_fname, 'w', **kwargs) as dst:
            dst.write_band(1, blue_ref_scaled.astype(rasterio.uint16))
            dst.write_band(2, green_ref_scaled.astype(rasterio.uint16))
            dst.write_band(3, red_ref_scaled.astype(rasterio.uint16))
            dst.write_band(4, nir_ref_scaled.astype(rasterio.uint16))

    else: # 8-band image
        with rasterio.open(raster_file_path) as src:
            band_coastalblue_radiance = src.read(1)            
        with rasterio.open(raster_file_path) as src:
            band_blue_radiance = src.read(2)
        with rasterio.open(raster_file_path) as src:
            band_green1_radiance = src.read(3)
        with rasterio.open(raster_file_path) as src:
            band_green_radiance = src.read(4)
        with rasterio.open(raster_file_path) as src:
            band_yellow_radiance = src.read(5)
        with rasterio.open(raster_file_path) as src:
            band_red_radiance = src.read(6)
        with rasterio.open(raster_file_path) as src:
            band_rededge_radiance = src.read(7)
        with rasterio.open(raster_file_path) as src:
            band_nir_radiance = src.read(8)

        # Multiply the Digital Number (DN) values in each band by the TOA reflectance coefficients
        band_coastalblue_reflectance = band_coastalblue_radiance * coeffs[1]
        band_blue_reflectance = band_blue_radiance * coeffs[2]
        band_green1_reflectance = band_green1_radiance * coeffs[3]
        band_green_reflectance = band_green_radiance * coeffs[4]
        band_yellow_reflectance = band_yellow_radiance * coeffs[5]
        band_red_reflectance = band_red_radiance * coeffs[6]
        band_rededge_reflectance = band_rededge_radiance * coeffs[7]
        band_nir_reflectance = band_nir_radiance * coeffs[8]

        # Write out the new raster having reflectance instead of radiance values
        # Set spatial characteristics of the output object to mirror the input
        kwargs = src.meta
        kwargs.update(dtype=rasterio.uint16, count = 8)

        # Scale values. See note next to scale definition at top of this fxn for more info.
        # This is apparently common practice.
        coastal_blue_ref_scaled = scale * band_coastalblue_reflectance
        blue_ref_scaled = scale * band_blue_reflectance
        green1_ref_scaled = scale * band_green1_reflectance
        green_ref_scaled = scale * band_green_reflectance
        yellow_ref_scaled = scale * band_yellow_reflectance
        red_ref_scaled = scale * band_red_reflectance
        rededge_ref_scaled = scale * band_rededge_reflectance
        nir_ref_scaled = scale * band_nir_reflectance

        # Write band calculations to a new raster file
        # NOTE: scaled to refl value [0-1] * 10000 to save as uint16
        with rasterio.open(refl_fname, 'w', **kwargs) as dst:
            dst.write_band(1, coastal_blue_ref_scaled.astype(rasterio.uint16))
            dst.write_band(2, blue_ref_scaled.astype(rasterio.uint16))
            dst.write_band(3, green1_ref_scaled.astype(rasterio.uint16))
            dst.write_band(4, green_ref_scaled.astype(rasterio.uint16))
            dst.write_band(5, yellow_ref_scaled.astype(rasterio.uint16))
            dst.write_band(6, red_ref_scaled.astype(rasterio.uint16))
            dst.write_band(7, rededge_ref_scaled.astype(rasterio.uint16))
            dst.write_band(8, nir_ref_scaled.astype(rasterio.uint16))
    
"""
Converts a Planet raster file's pixel radiance values to reflectance values
using the correction coefficients provided in an associated xml file
"""
def convert_radiance_to_reflectance(asset_type, raster_file_path, xml_coefficients_file_path):

    # get conversion coefficients for each band from xml file
    coeffs = get_conversion_coeffs(asset_type, xml_coefficients_file_path) 

    # read raster bands and convert using coeffs from above
    do_conversion(asset_type, raster_file_path, coeffs)  

    updated_f_path = get_updated_fname(raster_file_path)
    print('Radiance converted to reflectance for: {}'.format(updated_f_path)) 
    return updated_f_path

