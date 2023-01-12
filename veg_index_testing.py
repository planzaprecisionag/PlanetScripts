#%%
import pl_vegetation_index_lib as plvi

#%% TEST GET RASTER INFO FXN
file_path = r"C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3\5516798d-a973-4b24-bb5d-e81cd3ffb698\PSScene\20220918_154730_74_2414_3B_AnalyticMS_SR_clip.tif"
raster_info = plvi.get_raster_info(file_path)
print(raster_info)



# %%  TEST VEG INDEX CALCULATION
# indices_to_calculate = [
#     'ndvi', 
#     'evi',
#     'msavi'
#     ]

indices_to_calculate = [
    'msavi'
    ]

band_mappings = {
    "blue": 1,
    "green": 2,
    "red": 3,
    "nir": 4
}

file_path = r"C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3\5516798d-a973-4b24-bb5d-e81cd3ffb698\PSScene\20220918_154730_74_2414_3B_AnalyticMS_SR_clip.tif"

# test the vi calculation routines
plvi.calculate_vegetation_indices(file_path, indices_to_calculate, band_mappings)

print("Done")

# %% DEBUGGING - DELETE WHEN DONE
import rasterio
import numpy as np
import pl_vegetation_index_lib as plvi

raster_file_path = r"C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\Testing3\5516798d-a973-4b24-bb5d-e81cd3ffb698\PSScene\20220918_154730_74_2414_3B_AnalyticMS_SR_clip.tif"

raster_info = plvi.get_raster_info(file_path)

red = np.zeros(raster_info['shape'], dtype=rasterio.float32)
nir = np.zeros(raster_info['shape'], dtype=rasterio.float32)
ndvi = np.zeros(raster_info['shape'], dtype=rasterio.float32)

band_mappings = {
    "blue": 1,
    "green": 2,
    "red": 3,
    "nir": 4
}

# get individual band values necessary for the vi
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
    # 
    msavi = (2 * nir + 1 - np.sqrt((2 * nir + 1)**2 - 8 * (nir - red))) / 2
# %%
