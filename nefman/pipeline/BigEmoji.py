import pipeline
import backend
import command

import random
import re
import tinydb
from tinydb import TinyDB, Query

db = TinyDB('db/animate.json')
query = Query()

async def BigEmoji(message):

    #Remove this and log in a seperate pipeline
    print(message.content)

    #Don't remove messages with attachments, ever
    if(len(message.attachments) is not 0):
        return

    m = re.match('^(!)?\s?<:[a-zA-Z0-9]+:([0-9]+)>$', message.content)


    #No match?
    if m is None: return

    emoji_id = m.group(2)

    if m.group(1) == None:
        #Send a regular bigmoji
        await backend.cleanupMessage(message)

        await backend.sendResponse(message, type='image', url = f'https://cdn.discordapp.com/emojis/{emoji_id}.png')

    else:
        #Send an animated bigmoji
        overrides = db.search(query.id == emoji_id)

        if len(overrides) is 0:
            await backend.sendResponse(message, type='image', url = f'https://cdn.discordapp.com/emojis/{emoji_id}.png')
        else:
            url = random.choice(overrides)['to']
            if(re.match('.+-([a-zA-Z0-9]+)', url)):
                #await backend.sendResponse(message, type='image', url = f'https://media.giphy.com/media/{m.group(1)}/giphy.gif')
                await backend.sendResponse(message, url = url)
            else:
                await backend.sendResponse(message, url = url)



    #await backend.sendImage('', f'https://cdn.discordapp.com/emojis/{id}.png')



async def animate(req):
    m = re.match('^<:[a-zA-Z0-9]+:([0-9]+)>', req.arg)
    if m is None: return
    emoji_id = m.group(1)
    #await backend.cleanupMessage(req.message)

    image = backend.responseHistory.top(req.message).url

    db.insert({'id':emoji_id, 'to':image})

pipeline.append(BigEmoji)
command.append(animate,  'animate')
