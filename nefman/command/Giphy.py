import requests
import json

import command
import config
import backend
import message
import reaction

api_key = config.require('giphy', 'api_key')

async def Giphy(req):
    """Search Giphy"""

    query = req.arg

    r = requests.get(f'http://api.giphy.com/v1/gifs/search', params = {'q': query, 'api_key': api_key, 'limit': 100})

    if not r.ok:
        await backend.errorReact(req)
        return

    results = r.json()['data']


    url_list = []

    for res in results:
        url_list.append(res['url'])

    resp = await backend.sendResponse(req.message, text = url_list, url = url_list)

    await reaction.addCycleHandler(resp)
    await reaction.addMenuHandler(resp)

    #print json.dumps(data, sort_keys=True, indent=4)
    #print (r.json())



command.append(Giphy, ['gif', 'jif'])
