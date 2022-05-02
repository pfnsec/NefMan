import backend
import command
import reaction

import random
import re
import tinydb
from tinydb import TinyDB, Query

from fuzzywuzzy import fuzz
from fuzzywuzzy import process


class Game():
    def __init__(self, message):
        self.server  = message.server
        self.channel = message.channel
        self.user    = message.author
        self.players = []


symbols = {
    'join':'👥',
    'start':'✅'
}



async def NewGameHandlerCallback(reaction, user, game, removed=False):
    if(reaction.emoji == symbols['join']):
        if(removed):
            print(f'leave! {user}')
            if(user in game.players):
                game.players.remove(user)
        else:
            print(f'join! {user}')
            if(user not in game.players):
                game.players.append(user)


    elif(reaction.emoji == symbols['start']):
        print(f'start! {user}')
        await backend.clearReactions(reaction.message)
        await game.start()
        return True



async def addNewGameHandler(resp, game):
    await backend.emojiReact(resp.response, symbols['join'] )
    await backend.emojiReact(resp.response, symbols['start'])

    reaction.add(resp.response, NewGameHandlerCallback, game)

async def newGame(req):

    print(req.message.author)
    author = req.message.author.display_name

    results = process.extract(req.arg, games.keys())

    print(results)

    #Too crappy to match
    if(results[0][1] <= 50):
        resp = await backend.sendResponse(req.message, text=f'{games.keys()}')
        return

    name = results[0][0]

    game = games[name](req.message)

    resp = await backend.sendResponse(req.message, text=f'New game! press 👥 to join; {author}, press ✅ to start!')

    await addNewGameHandler(resp, game)


async def gameList(req):
    resp = await backend.sendResponse(req.message, text=f'{games.keys()}')
    return


command.append(newGame, 'newgame')
command.append(gameList, 'gamelist')


games = {}

def append(game, name):
    games[name] = game


import command.NefGames

