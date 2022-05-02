import config
import command
import backend
import reaction

import pprint
import apiclient
import apiclient.discovery
import apiclient.errors


from apiclient.discovery import build
from apiclient.errors    import HttpError
from oauth2client.tools  import argparser


DEVELOPER_KEY = config.require("google", "yt_key")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
    search_response = youtube.search().list(
        q=query,
        type='video',
        part="id,snippet",
        maxResults=25
    ).execute()

  # Select only videos
    #items = [r for r in search_response.get("items", []) if r["id"]["kind"] == "youtube#video"]
    items = search_response.get("items", [])

    id_list = [r["id"]["videoId"] for r in items]
    url_list = [f'https://youtube.com/watch?v={id}' for id in id_list]

    title_list = [r['snippet']['title'] for r in items]

    return url_list, title_list

async def channel_search(req):
    query = req.arg

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
    search_response = youtube.search().list(
        q=query,
        type='channel',
        part="id,snippet",
        maxResults=25
    ).execute()

  # Select only videos
    #items = [r for r in search_response.get("items", []) if r["id"]["kind"] == "youtube#video"]
    items = search_response.get("items", [])

    id_list = [r["id"]["channelId"] for r in items]

    url_list = [f'https://www.youtube.com/channel/{id}' for id in id_list]

    #title_list = [r['snippet']['title'] for r in items]

    resp = await backend.sendResponse(req.message, url = url_list)
    await reaction.addCycleHandler(resp)

async def run(req):
    url_list, _ = youtube_search(req.arg)
    resp = await backend.sendResponse(req.message, url = url_list)
    await reaction.addCycleHandler(resp)

command.append(run, 'yt')
command.append(channel_search, 'ytchan')
