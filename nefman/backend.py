import discord
import asyncio
from pprint import pprint
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import requests

import config
import pipeline
import reaction
import command
import message

client = []

client = discord.Client()

#Discord Event Handlers

@client.event
async def on_ready():
    global clientUser
    global errorEmoji
    global successEmoji

    clientUser = client.user
    print('Logged In')

    error   = config.lookup('discord', 'error_emoji')
    success = config.lookup('discord', 'success_emoji')

    # MIG
    #emojis  = client.get_all_emojis()
    emojis = []

    for em in emojis:
        if error == em.name:
            errorEmoji = em

        if success == em.name:
            successEmoji = em



@client.event
async def on_message(message):
    global clientUser

    #ignore the bot's own messages
    if(message.author.id == clientUser.id):
        return

    requestHistory.push(message)

    await pipeline.run(message)

@client.event
async def on_message_edit(old_message, message):
    global clientUser

    #ignore the bot's own edits
    if(message.author.id == clientUser.id):
        return


    old_top = responseHistory.top(old_message)


    await pipeline.run(message)

    #Delete the previous top response if we're about to issue another one on edit
    if old_top is not None and old_top.request == message:
        old_resp = old_top.response
        await old_resp.delete_message()


@client.event
async def on_message_delete(message, **kwargs):
    pass


@client.event
async def on_server_role_update(before, after):
    pass


@client.event
async def on_reaction_add(react, user):
    global clientUser

    #ignore the bot's own reactions
    if(user.id == clientUser.id):
        return

    print(react.emoji)

    found = await reaction.run(react, user, removed=False)

    if(found):
        await react.message.remove_reaction(react.emoji, user)


@client.event
async def on_reaction_remove(react, user):
    global clientUser

    #ignore the bot's own reactions
    if(user.id == clientUser.id):
        return

    await reaction.run(react, user, removed=True)


def run():
    client.run(config.require('discord', 'api_key'))


requestHistory  = message.History()
responseHistory = message.History()

globalResponseHistory = message.History()


#Text Channel Interface


async def sendResponse(request, text='', type='text', url=None, fp=None):
    response = message.Response(request, text=text, kind=type, url=url, fp=fp)

    if response is None:
        return

    responseHistory.push(response)

    await response.send()

    return response


async def sendPackedResponse(response):
    if response is None:
        return

    responseHistory.push(response)

    await response.send()

    return response


def getTopResponse(request):
    return responseHistory.global_top(request)



#Elaborate messages

async def sendMessage(channel, body, **kwargs):
    return await channel.send(body, **kwargs)

async def editMessage(msg, body, embed=None, **kwargs):
    if(embed):
        print(embed)
        ret = await msg.edit(embed=embed)
    else:
        ret = await msg.edit(content=body)
    
    print(ret)

    return msg

async def sendFile(channel, fp, **kwargs):
    return await channel.send(file=fp)



#Called by commands to clean up the messages that triggered them
async def cleanupMessage(message):
    await message.delete()

async def cleanupRequest(message):
    await requestHistory.pop(message).delete()
    await requestHistory.pop(message).delete()

async def cleanupResponse(message):
    await responseHistory.top(message).request.delete()
    await responseHistory.pop(message).response.delete()
    await responseHistory.pop(message).response.delete()


#Re-run the pipeline on an already received message
async def recycle(message):
   # await client.delete_message(responseHistory.pop(message.author).response)
    resp = responseHistory.pop(message)
    print(resp)
    resp.delete()
    await pipeline.run(resp.request)


#Call the cycle methods on the message author's last response 
async def cycleForward(message):
    await responseHistory.top(message).cycleForward()

async def cycleBackward(message):
    await responseHistory.top(message).cycleBackward()



#Emoji Reactions, including error/success

async def emojiReact(message, emoji):
    await message.add_reaction(emoji)
    
async def emojiUnreact(message, emoji):
    await message.remove_reaction(emoji, message.author)


async def successReact(message):
    await message.add_reaction(successEmoji)

async def errorReact(message):
    await message.add_reaction(errorEmoji)

async def clearReactions(message):
    await message.clear_reactions()


#User info lookup

def getRoleByID(message, id):
    """Returns role name"""
    members = message.channel.guild.members

    roleList = [m.top_role.name for m in members if m.id == id]
    return roleList[0]


def getNickByID(message, id):
    """Returns current nickname"""
    members = message.channel.guild.members

    nickList = [m.nick for m in members if m.id == id]
    return nickList[0]


from pprint import pprint
async def lookupNick(message, nick):
    """Fuzzy nickname search. Also works if the nick is a role name
       and the role has only one user."""

    print("lookupNick:", nick)
    print(message.channel)
    print(message.channel.guild)
    pprint(message.channel.guild.members)

    members = message.channel.guild.members

    nameList = [(m.name, m) for m in members]
    nickList = [(m.nick, m) for m in members]
    roleList = [(m.top_role.name, m) for m in members]

    lkup = dict()
    lkup.update(dict(nameList))
    lkup.update(dict(nickList))
    lkup.update(dict(roleList))

    results = process.extract(nick, lkup.keys())

    #print(results)

    #Too crappy to match
    if(results[0][1] <= 50):
        #return False
        return None

    #if top two scores (r[:][1]) are the same AND 
    #they don't refer to the same person (r[:][0]),
    #it's ambiguous.
    elif(results[0][1] == results[1][1] and
         results[0][0] != results[1][0] and
         results[0][1] <= 90):
        return None

    else:
        return lkup[results[0][0]]


#Server properties

async def setServerTitle(request):
    guild = request.message.guild
    await guild.edit(name=request.arg)

async def setServerImage(request):
    guild = request.message.guild
    top    = responseHistory.top(request.message)

    if(len(top.response.attachments) is not 0):
        image = top.response.attachments[0]['url']
    else:
        image  = top.url

    print(image)

    r = requests.get(image)

    if not r.ok:
        print('{r.status_code} - {r.reason} - {r.text}')
        await errorReact(request.message)
    else:
        await guild.edit(icon=r.content)


async def createEmoji(request):
    """Create an emoji with a given name"""

    image = responseHistory.top(request.message).url

    r = requests.get(image)

    if not r.ok:
        print('{r.status_code} - {r.reason} - {r.text}')
        await errorReact(request.message)
    else:
        guild = request.message.guild
        await guild.create_custom_emoji(name=request.arg, image=r.content)


async def setAvatar(request, user):
    """Sets the Bot's avatar image."""

    image = responseHistory.top(request.message).url

    r = requests.get(image)

    if not r.ok:
        print('{r.status_code} - {r.reason} - {r.text}')
        await errorReact(request.message)
    else:
        await clientUser.edit(avatar=r.content)

async def setNick(user, nick):
    """Sets a user's nickname."""
    #await client.change_nickname(clientUser, nick)
    if user is None:
        user = currentAuthor

    await user.edit(nick=nick)

async def setColour(server, role, colour):
    print("setColour", colour, discord.Colour(colour))
    await role.edit(colour=discord.Colour(colour))


async def setStatus(text, url=None):

    game = discord.Game(name=text, url=url, type=1)

    await client.change_presence(game=game)


async def kick(user):
    await client.kick(user)


#Util function to return the user's last result
def UserStackTop(req):
    return responseHistory.top(req.message)
