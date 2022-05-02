import backend
import pipeline
import command

import random
import pprint


random.seed()

async def manual(req):
    """Display this man page"""
    await backend.sendResponse(req.message, text=command.man(req.arg))

async def server(req):
    """Show the full-size server icon"""
    server = req.message.guild
    await backend.sendResponse(req.message, type='image', url = server.icon_url)

async def avatar(req):
    """Show the full-size avatar of a user"""
    user = await backend.lookupNick(req.message, req.arg)
    if not user:
        await backend.errorReact(req.message)
        return
    await backend.sendResponse(req.message, type='image', url = user.avatar_url)

async def botimg(req):
    """Set the bot's avatar"""
    if(len(req.args) > 0):
        user = await backend.lookupNick(req.message, req.arg)
        if not user:
            await backend.errorReact(req.message)
            return
    else:
        user = None

    await backend.setAvatar(req, user)

async def title(req):
    """Set the server title"""
    await backend.setServerTitle(req)


async def img(req):
    """Set the server image"""
    await backend.setServerImage(req)

async def colour(req):
    """Set a user's colour"""

    #No arguments; Set the author's colour randomly
    if(len(req.args)) == 0:
        colour = random.randint(0, 2 ** 24 -1)
        user = req.message.author

    else:

        #Figure out if the first argument is a user...
        r = await backend.lookupNick(req.message, req.args[0])

        if r is not None:
            user = r

            if(len(req.args) == 2):
                colour = int(req.args[1], 16)
            else:
                colour = random.randint(0, 2 ** 24 -1)
        else:
            user = req.message.author
            colour = int(req.args[0], 16)


    role = user.top_role


    await backend.setColour(req.message.server, role, colour)

async def nick(req):
    """Set a users nickname"""
    r = await backend.lookupNick(req.message, req.args[0])

    if r is None:
        await backend.errorReact(req.message)
    elif r is False:
        await backend.setNick(None, req.arg)
    else:
        await backend.setNick(r, ' '.join(req.args[1:]))


async def emoji(req):
    """Add last image result as a new emoji"""
    await backend.createEmoji(req)

command.append(manual, 'man')
command.append(avatar, 'avatar')
command.append(server, 'server')
command.append(botimg, 'botimg')
command.append(title,  'title')
command.append(img,    'img')
command.append(nick,   'nick')
command.append(colour, 'colour')
command.append(colour, 'color')

command.append(emoji,  'emoji')
