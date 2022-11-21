#%%
import pl_convert_planet_radiance_to_reflectance as pl_convert

#%%
raster_path = r'C:\Users\P\Pictures\PythonTestDownloads\PlanetImageryAndXML\20211029_150146_74_2449_3B_AnalyticMS_8b.tif'
xml_path = r'C:\Users\P\Pictures\PythonTestDownloads\PlanetImageryAndXML\20211029_150146_74_2449_3B_AnalyticMS_8b_metadata.xml'
updated_f_path = pl_convert.convert_radiance_to_reflectance('OrthoAnalytic_8b', raster_path, xml_path)
print('Conversion complete: {}'.format(updated_f_path))
# %%
