#%% imports

import json
import os
import pathlib
import time
import numpy as np
from planet import Auth, reporting
from planet import Session, DataClient, OrdersClient
import rasterio
from rasterio.plot import show
import requests
from  datetime import datetime
from planet_json_utils import p
import planet_raster_downloader as prd_v1

#%%
# API Key stored as an env variable
# if your Planet API Key is not set as an environment variable, you can paste it below
if os.environ.get('PL_API_KEY', ''):
    API_KEY = os.environ.get('PL_API_KEY', '')
else:
    API_KEY = 'PASTE_API_KEY_HERE'

# construct auth tuple for use in the requests library
BASIC_AUTH = (API_KEY, '')

# Setup the session
session = requests.Session()

# Authenticate
session.auth = (API_KEY, "")

# Establish headers & Orders URL
headers = {'content-type': 'application/json'}
orders_url = 'https://api.planet.com/compute/ops/orders/v2'

#%%# define products part of order
single_product = [
    {
      "item_ids": ["20151119_025740_0c74"],
      "item_type": "PSScene",
      "product_bundle": "analytic_udm2"
    }
]

same_src_products = [
    {
      "item_ids": ["20151119_025740_0c74",
                   "20151119_025739_0c74"],
      "item_type": "PSScene",
      "product_bundle": "analytic_udm2"
    }
]

multi_src_products = [
    {
      "item_ids": ["20151119_025740_0c74"],
      "item_type": "PSScene",
      "product_bundle": "analytic_udm2"
    },
    {
      "item_ids": ["LC81330492015320LGN01"],
      "item_type": "Landsat8L1G",
      "product_bundle": "analytic"
    },
    
]

#%% fxn defs
# PL - updated to pass download save dir param 1/5/2023
async def poll_and_download(order, download_root_dir):
    retry_delay_seconds = 60
    async with Session() as sess:
        cl = OrdersClient(sess)

        # Use "reporting" to manage polling for order status
        with reporting.StateBar(state='creating') as bar:
            # Grab the order ID
            bar.update(state='created', order_id=order['id'])

            # poll...poll...poll...
            await cl.wait(order['id'], callback=bar.update_state, delay=retry_delay_seconds)

        # if we get here that means the order completed. Yay! Download the files.
        filenames = await cl.download_order(order_id=order['id'], directory=download_root_dir)
# define helpful functions for visualizing downloaded imagery
def show_rgb(img_file):
    with rasterio.open(img_file) as src:
        b,g,r,n = src.read()

    rgb = np.stack((r,g,b), axis=0)
    show(rgb/rgb.max())
    
def show_gray(img_file):
    with rasterio.open(img_file) as src:
        g = src.read(1)
    show(g/g.max())

#%% no processing example
#%%
async def do_download_example():
    request = {
    "name": "no processing",
    "products": single_product,
    }

    #%%# allow for caching, replace this with your image file
    img_file = 'data/50df6201-ea94-48f1-bec9-65dd9cd8354b/1/files/PSScene/20151119_025740_0c74/analytic_udm2/20151119_025740_0c74_3B_AnalyticMS.tif'
    img_file

    #%%
    if not os.path.isfile(img_file):
        async with Session() as sess:
            cl = OrdersClient(sess)
            order = await cl.create_order(request)
            # PL - the class appears to be missing any poll_and_download method.... 
            # updating my call to use cl.download_order
            download = await cl.poll_and_download(order)
        img_file = next(download[d] for d in download
                        if d.endswith('_3B_AnalyticMS.tif'))
    print(img_file)

#%% clip example - had to move everything inside of fxn to avoid errors on async with calls
async def do_clip_example():
    clip_aoi = {
        "type":"Polygon",
        "coordinates":[[[94.81858044862747,15.858073043526062],
                        [94.86242249608041,15.858073043526062],
                        [94.86242249608041,15.894323164978303],
                        [94.81858044862747,15.894323164978303],
                        [94.81858044862747,15.858073043526062]]]
    }
    # %%
    # define the clip tool
    clip = {
        "clip": {
            "aoi": clip_aoi
        }
    }
    # %%
    # create an order request with the clipping tool
    request_clip = {
    "name": "just clip",
    "products": single_product,
    "tools": [clip]
    }

    request_clip
    # %%
    # allow for caching so we don't always run clip
    run_clip = True

    clip_img_file = 'data/6c23f9e1-d86a-47fe-9eb2-2693196168e0/1/files/20151119_025740_0c74_3B_AnalyticMS_clip.tif'
    if os.path.isfile(clip_img_file): run_clip = False
    # %%
    if run_clip:
        async with Session() as sess:
            cl = OrdersClient(sess)
            order = await cl.create_order(request_clip)
            # download = await poll_and_download(order)
            downloaded_clip_files = await poll_and_download(order) # pl changed, maybe was a typo/bug in example
        clip_img_file = next(downloaded_clip_files[d] for d in downloaded_clip_files
                        if d.endswith('_3B_AnalyticMS_clip.tif'))
    clip_img_file
    # %%
    # show_rgb(img_file)
    show_rgb(clip_img_file)

async def order_and_download_clipped_rasters(clip_aoi_geom, file_save_path, item_type, product_bundle, product_id_list, planet_api_key, debug=False):
    # PL - 1/6/2023
    # note: had to update the planet orders.py lib to replace the dl location url
    # ln 269:
    # updated_location = location.replace(r'https://api.planet.com/compute/ops/download/', r'https://link.planet.com/orders/v2/download')
    # this successfully downloaded the orders

    # Setup the session
    session = requests.Session()

    # Authenticate
    session.auth = (planet_api_key, "")
    
    # define the clip tool
    clip = {
        "clip": {
            "aoi": clip_aoi_geom
        }
    }

    #define products 
    products = {
        "item_ids": product_id_list,
        "item_type": item_type,
        "product_bundle": product_bundle
    }

    # create an order request with the clipping tool
    timestamp = datetime.now()
    order_name = 'ClippedOrder_{}'.format(str(timestamp))
    request_clip = {
    "name": order_name,
    "source_type": "scenes",
    "products": [products],
    "tools": [clip]
    }

    if debug:
        print('Request Clip:')
        p(request_clip)
        print()

    # allow for caching so we don't always run clip
    run_clip = True
    if run_clip:
        async with Session() as sess:
            cl = OrdersClient(sess)
            order = await cl.create_order(request_clip)
            # PL - 1/6/2023 
            # fixed issue with dl link redirecting to new url and preventing dl
            # TODO: (if neccessary): update code to detect redirect, extract new url from
            # response and use that to dl assets. For now, using a hard-coded updated base-url
            # is working

            download = await poll_and_download(order, download_root_dir=file_save_path)
    #         downloaded_clip_files = await poll_and_download(order, file_save_path) # pl changed from line above
    # clip_img_file = next(downloaded_clip_files[d] for d in downloaded_clip_files
    #                     if d.endswith('_clip.tif'))
            return order

async def download_order(order_id, download_root_dir, planet_api_key, debug=False):
    # download planet rasters, metadata, etc based upon order id
    # 1. try to download order via Planet lib
    # method def:
    # async def download_order(self,
        #  order_id: str,
        #  directory: Path = Path('.'),
        #  overwrite: bool = False,
        #  progress_bar: bool = False,
        #  checksum: str = None) -> typing.List[Path]:
    # Setup the session
    session = requests.Session()
    # Authenticate
    session.auth = (planet_api_key, "")
    filenames = ['no files']
    async with Session() as sess:
        cl = OrdersClient(sess)
        # Use "reporting" to manage polling for order status
        with reporting.StateBar(state='creating') as bar:
            # Grab the order ID
            bar.update(state='created', order_id=order_id)

            # poll...poll...poll...
            # await cl.wait(order_id, callback=bar.update_state, delay=5)

            # if we get here that means the order completed. Yay! Download the files.
            filenames = await cl.download_order(order_id=order_id, directory=download_root_dir)
    
    print('DONE')
    return filenames