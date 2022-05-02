import command
import message
import backend

import pokebase as pb

async def Pokedex(req):

    await backend.sendResponse(req.message, url=f'https://www.pokemon.com/us/pokedex/{req.arg}')

command.append(Pokedex, ['dex'])
