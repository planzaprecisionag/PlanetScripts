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
async def poll_and_download(order):
    async with Session() as sess:
        cl = OrdersClient(sess)

        # Use "reporting" to manage polling for order status
        with reporting.StateBar(state='creating') as bar:
            # Grab the order ID
            bar.update(state='created', order_id=order['id'])

            # poll...poll...poll...
            await cl.wait(order['id'], callback=bar.update_state)

        # if we get here that means the order completed. Yay! Download the files.
        filenames = await cl.download_order(order['id'])
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