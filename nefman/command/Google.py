import config
import command
import backend
import pipeline
import reaction
import requests

from pprint import pprint
import re

import apiclient
import apiclient.discovery
import apiclient.errors


from apiclient.discovery import build
from apiclient.errors    import HttpError
from oauth2client.tools  import argparser


azure_key = config.require("azure", "sub_key")

key = config.require("google", "yt_key")
cx = config.require("google", "cx")
image = build("customsearch", "v1",
    developerKey=key)

def image_search(query):

  # Call the search.list method to retrieve results matching the specified
  # query term.
    search_response = image.cse().list(
        q=query,
        searchType='image',
        cx=cx
    ).execute()

    items = search_response['items']

    urls = [u['link'] for u in items]

    return urls

def snippet_search(query):

  # Call the search.list method to retrieve results matching the specified
  # query term.
    search_response = image.cse().list(
        q=query,
        #searchType='image',
        cx=cx
    ).execute()

#    pprint(search_response)

    items = search_response['items']

    urls = [u['link'] for u in items]

    return urls

async def info(req):
    """Search Google Images"""
    url_list = snippet_search(req.arg)
    resp = await backend.sendResponse(req.message, url = url_list)
    await reaction.addCycleHandler(resp)
    await reaction.addMenuHandler(resp)

async def gl(req):
    """Search Google Images"""
    url_list = image_search(req.arg)
    #resp = await backend.sendResponse(req.message, type='image', url = url_list)
    resp = await backend.sendResponse(req.message, type='text', url = url_list)

    await reaction.addCycleHandler(resp)
    await reaction.addMenuHandler(resp)

async def test(message):
    m = re.match('(.*).jp.g', message.content)
    if m is None: return

    name = m.group(1)
    print(f'name:{name}')
    url_list = image_search(name)
    await backend.sendResponse(req.message, type='image', url = url_list)

async def bing(req):
    """Search Bing Images"""

    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key" : azure_key}
    params  = {"q": req.message}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    thumbnail_urls = [img["thumbnailUrl"] for img in search_results["value"][:16]]
    print(thumbnail_urls)

    resp = await backend.sendResponse(req.message, type='text', url = thumbnail_urls)


command.append(gl, 'gl')
command.append(bing, 'bing')
command.append(info, 'info')
