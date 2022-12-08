#%% Library imports
from planet_raster_downloader import get_planet_download_stats, download_planet_rasters
import planet_credentials as plc
#%% Getting param values to pass to stats and dl fxns
# TODO: make form to capture these values
download_root_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\PlanetRasters\2022'
item_types = ['PSScene']
asset_type = 'ortho_analytic_4b_sr'
planet_api_key = plc.get_planet_api_key()
planet_base_url = "https://api.planet.com/data/v1"
img_start_date_string = "2022-04-01T00:00:00.000Z"
img_end_date_string = "2022-10-31T00:00:00.000Z"
cloud_cover_percent_max = 0.8

# root dir holding field boundary polygons. will loop through this and pull
# planet rasters using these as AOI's
field_aoi_dir = r'C:\Users\P\Box\Phillip\OFE Biologicals\QGIS\FieldPolygons\FieldAOIsForPlanetDownload'


#%% check stats for query (how many images, etc)
get_planet_download_stats()

#%% Do the download
download_planet_rasters()