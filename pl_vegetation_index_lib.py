#%% import libs
import os
import rasterio
import numpy as np

#%% function defs
def get_raster_info(raster_file_path):
    # create dict to hold raster metadata 
    raster_info = {
        'band_count':-1,
        'crs': None,
        'width': -1,
        'height': -1,
        'bounds': None,
        'band_no_data_values': None
    }
    with rasterio.open(raster_file_path) as raster:
        raster_info['band_count'] = raster.count
        raster_info['crs'] = raster.crs
        raster_info['width'] = raster.width
        raster_info['height'] = raster.height
        raster_info['bounds'] = raster.bounds
        raster_info['band_no_data_values'] = raster.nodatavals
        raster_info['shape'] = raster.shape
    return raster_info

def generate_vegetation_index_rasters(raster_file_path, indices_to_calculate, band_mappings: dict):
    # get raster metadata
    raster_info  = get_raster_info(raster_file_path)

    #TODO: another index: Spectral Vegetation Index (from 8-band)
    # spectral vegetation index (ρNIR − ρSWIR)/(ρNIR + ρSWIR), where ρNIR and ρSWIR are the near-infrared (NIR) and shortwave-infrared (SWIR) reflectances, respectively, has been widely used to indicate vegetation moisture condition

    # not doing this anymore, writing separate files for each vi now
    # to make it easier to code and easier to interpret what each vi
    # raster contains
    # # band index dict for new image
    # vi_band_indices = {
    #         'ndvi': 1,
    #         'evi': 2,
    #         'msavi': 3,
    #         'ndre': 4,
    #         'ccci': 5
    #     }
    # int to keep track of new image's band count
    # i_vi_count = 0

    if 'NDVI' in indices_to_calculate or 'ndvi' in indices_to_calculate:
        # calculate NDVI and add as band in new raster

        # instantiate kwargs var to keep it within scope outside of with block
        kwargs = None

        # new raster name (hard coded to work for tifs only right now)
        ndvi_file_path = raster_file_path.replace('.tif', '_ndvi.tif')
        
        # increment band counter
        # i_vi_count = i_vi_count + 1

        red = np.zeros(raster_info['shape'], dtype=rasterio.float32)
        nir = np.zeros(raster_info['shape'], dtype=rasterio.float32)
        ndvi = np.zeros(raster_info['shape'], dtype=rasterio.float32)

        # get individual band values necessary for the vi
        with rasterio.open(raster_file_path) as img:
            red = img.read(band_mappings['red']).astype('float')   
            nir = img.read(band_mappings['nir']).astype('float')

        # set masked values to nan
        red[red==0] = np.nan
        nir[nir==0] = np.nan
        # Write out the new raster having reflectance instead of radiance values
        # Set spatial characteristics of the output object to mirror the input
        kwargs = img.meta
        # update band count to be single band
        kwargs.update(dtype=rasterio.float32, count = 1)

        #calculate vi
        ndvi = (nir - red)/(nir + red)

        #add new band to new image and write file
        if not os.path.exists(ndvi_file_path):
            try:
                with rasterio.open(ndvi_file_path, 'w', decimal_precision=16, **kwargs) as dst:
                    dst.write_band(1, ndvi)
                print('Wrote NDVI file to: {}'.format(ndvi_file_path))
            except:
                print('Error writing NDVI file for {}'.format(ndvi_file_path))
        else:
            print('WARNING: NDVI File already exists. Delete it and rerun this to recreate.')
            print(ndvi_file_path)
    if 'EVI' in indices_to_calculate or 'evi' in indices_to_calculate:
        # calculate EVI and add as band in new raster
        # define evi coeffiecients, apparently they are the same for all
        # satellites
        evi_c1 = 6
        evi_c2 = 7.5
        evi_l = 1
        evi_g = 2.5

        # instantiate kwargs var to keep it within scope outside of with block
        kwargs = None

        # new raster name (hard coded to work for tifs only right now)
        evi_file_path = raster_file_path.replace('.tif', '_evi.tif')

        evi = None

        # get individual band values necessary for the vi
        with rasterio.open(raster_file_path) as img:
            red = img.read(band_mappings['red']).astype('float')  
            nir = img.read(band_mappings['nir']).astype('float')  
            blue = img.read(band_mappings['blue']).astype('float')  

            # Write out the new raster having reflectance instead of radiance values
            # Set spatial characteristics of the output object to mirror the input
            kwargs = img.meta
            # update band count to be single band
            kwargs.update(dtype=rasterio.float32, count = 1)

            # set masked values to nan
            red[red==0] = np.nan
            nir[nir==0] = np.nan
            blue[blue==0] = np.nan

            #calculate vi
            evi = evi_g * ((nir - red) / (nir + evi_c1 * red - evi_c2 * blue + evi_l))

        #add new band to new image and write file
        if not os.path.exists(evi_file_path):
            try:
                with rasterio.open(evi_file_path, 'w', decimal_precision=16, **kwargs) as dst:
                    dst.write_band(1, evi)
            except:
                    print('Error writing EVI file for {}'.format(evi_file_path))
        else:
            print('WARNING: EVI File already exists. Delete it and rerun this to recreate.')
            print(evi_file_path)

    if 'MSAVI' in indices_to_calculate or 'msavi' in indices_to_calculate:
        # MSAVI good for limited canopy coverage (ie season start and end)
        # formula:
        # (2 * NIR + 1 – sqrt ((2 * NIR + 1)2 – 8 * (NIR - R))) / 2
        # values and rough interpretation: 
        # -1 to 0.2: bare soil
        # 0.2 to 0.4: germination, little veg cover
        # 0.4 to 0.6: leaf development stage
        # > 0.6: less meaningful, switch to NDVI, EVI, NDRE etc

        # instantiate kwargs var to keep it within scope outside of with block
        kwargs = None

        # new raster name (hard coded to work for tifs only right now)
        msavi_file_path = raster_file_path.replace('.tif', '_msavi.tif')

        msavi = None

        # get individual band values necessary for the vi
        with rasterio.open(raster_file_path) as img:
            red = img.read(band_mappings['red']).astype('float')  
            nir = img.read(band_mappings['nir']).astype('float')  
            
            # Write out the new raster having reflectance instead of radiance values
            # Set spatial characteristics of the output object to mirror the input
            kwargs = img.meta
            # update band count to be single band
            kwargs.update(dtype=rasterio.float32, count = 1)

            # set masked values to nan
            red[red==0] = np.nan
            nir[nir==0] = np.nan

            #calculate vi
            # NOTE: Python interprets ^ as XOR, use ** to raise something to a power
            msavi = (2 * nir + 1 - np.sqrt((2 * nir + 1)**2 - 8 * (nir - red))) / 2

        #add new band to new image and write file
        if not os.path.exists(msavi_file_path):
            try:
                with rasterio.open(msavi_file_path, 'w', decimal_precision=16, **kwargs) as dst:
                    dst.write_band(1, msavi)
            except:
                    print('Error writing MSAVI file for {}'.format(msavi_file_path))
        else:
            print('WARNING: MSAVI File already exists. Delete it and rerun this to recreate.')
            print(msavi_file_path)

    if 'NDRE' in indices_to_calculate or 'ndre' in indices_to_calculate:
        # ndre - good for fuller canopy (ie mid to late mid season when ndvi may saturate)
        # verify that red edge present in bands
        if 'RE' or 're' in band_mappings:
            # calculate NDRE
            # instantiate kwargs var to keep it within scope outside of with block
            kwargs = None

            # new raster name (hard coded to work for tifs only right now)
            ndre_file_path = raster_file_path.replace('.tif', '_ndre.tif')

            ndre = None

            # get individual band values necessary for the vi
            with rasterio.open(raster_file_path) as img:
                red = img.read(band_mappings['red'])
                re = img.read(band_mappings['re'])
                # Write out the new raster having reflectance instead of radiance values
                # Set spatial characteristics of the output object to mirror the input
                kwargs = img.meta
                # update band count to be single band
                kwargs.update(dtype=rasterio.float32, count = 1)

                #calculate vi
                ndre = (re - red) / (re + red)

            #add new band to new image and write file
            if not os.path.exists(ndre_file_path):
                try:
                    with rasterio.open(ndre_file_path, 'w', decimal_precision=16, **kwargs) as dst:
                        dst.write_band(1, ndre)
                except:
                        print('Error writing NDRE file for {}'.format(ndre_file_path))
            else:
                print('WARNING: NDRE File already exists. Delete it and rerun this to recreate.')
                print(ndre_file_path)
        else:
            print('WARNING: CANNOT CALCULATE NDRE WITHOUT RED EDGE BAND')
    if 'CCCI' in indices_to_calculate or 'ccci' in indices_to_calculate:
        # CCCI = NDRE / NDVI
        # verify that red edge present in bands
        if 'RE' or 're' in band_mappings:
            # calculate NDRE
            # instantiate kwargs var to keep it within scope outside of with block
            kwargs = None

            # new raster name (hard coded to work for tifs only right now)
            ccci_file_path = raster_file_path.replace('.tif', '_ccci.tif')

            ccci = None

            # get individual band values necessary for the vi
            with rasterio.open(raster_file_path) as img:
                red = img.read(band_mappings['red'])
                nir = img.read(band_mappings['nir'])
                re = img.read(band_mappings['re'])
                # Write out the new raster having reflectance instead of radiance values
                # Set spatial characteristics of the output object to mirror the input
                kwargs = img.meta
                # update band count to be single band
                kwargs.update(dtype=rasterio.float32, count = 1)

                #calculate vi
                ndre = (re - red) / (re + red)
                ndvi = (nir - red) / (nir + red)
                ccci = ndre / ndvi
            #add new band to new image and write file
            if not os.path.exists(ccci_file_path):
                try:
                    with rasterio.open(ccci_file_path, 'w', decimal_precision=16, **kwargs) as dst:
                        dst.write_band(1, ccci)
                except:
                        print('Error writing CCCI file for {}'.format(ccci_file_path))
            else:
                print('WARNING: CCCI File already exists. Delete it and rerun this to recreate.')
                print(ccci_file_path)
        else:
            print('WARNING: CANNOT CALCULATE CCCI WITHOUT RED EDGE BAND')