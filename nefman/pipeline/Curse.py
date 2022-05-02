
import pprint
import tinydb
from tinydb import TinyDB, Query
import random

import command
import backend
import pipeline


random.seed()

def ColourDelta(colour):

    magnitude = 50

    component = random.choice([0, 1, 2])

    if(colour[component] == 0):
        sign =  1
    elif(colour[component] == 255):
        sign = -1
    else:
        sign = random.choice([-1, 1])

    colour[component] += sign * magnitude
    colour[component] = colour[component] % 255

    return colour

async def curseEffect(message):
    role = message.author.top_role

    colour = role.colour.to_rgb()

    colour = list(colour)

    colour = ColourDelta(colour)

    hex_colour = colour[2] + (colour[1] << 8) + (colour[0] << 16)

    await backend.setColour(message.guild, role, hex_colour)


pipeline.append(curseEffect)

