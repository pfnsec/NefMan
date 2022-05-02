
import config
import command
import backend
import pipeline

import re
import random

random.seed()


async def MatchDiceEmoji(message):
    m = re.match('^(!)?\s?<:[a-zA-Z0-9]+:([0-9]+)>', message.content)


async def roll(req):
    if(len(req.args) > 0):
        n = int(req.args[0])
    else:
        n = 20

    value = random.randint(1, n)

    resp = str(value)

    resp = resp.replace('0', ' :zero:')
    resp = resp.replace('1', ' :one:')
    resp = resp.replace('2', ' :two:')
    resp = resp.replace('3', ' :three:')
    resp = resp.replace('4', ' :four:')
    resp = resp.replace('5', ' :five:')
    resp = resp.replace('6', ' :six:')
    resp = resp.replace('7', ' :seven:')
    resp = resp.replace('8', ' :eight:')
    resp = resp.replace('9', ' :nine:')


    await backend.sendResponse(req.message, resp)



async def vote(req):
    await backend.emojiReact(req.message, '⬆')
    await backend.emojiReact(req.message, '⬇')




pipeline.append(MatchDiceEmoji)
command.append(roll, 'roll')
command.append(vote, 'vote')
