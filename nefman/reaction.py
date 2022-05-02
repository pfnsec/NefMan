
import config
import backend

class ReactHandler:
    def __init__(self, message, callback, callback_var):
        self.message = message
        self.callback = callback
        self.callback_var = callback_var

    async def run(self, reaction, user, removed=False):
        return await self.callback(reaction, user, self.callback_var, removed=removed)


items = []
limit = int(config.lookup('discord', 'history_size')) or 30

def add(message, callback, callback_var):

    if(len(items) == limit):
        items.pop(0)

    items.append(ReactHandler(message, callback, callback_var))


async def run(reaction, user, removed=False):
    #return whether or not any handlers were found.
    found = False

    for i in items:
        if(i.message.id == reaction.message.id):
            #...Handlers return false if they don't want the reaction to be removed.
            if(await i.run(reaction, user, removed=removed)):
                found = True

    return found


symbols = {
    'back':'⏪',
    'forward':'⏩',
    'menu':'💬',
    'delete':'🗑',
    'img' : '🖼',
}



async def CycleHandlerCallback(reaction, user, response, removed=False):
    if(response.author.id != user.id):
        return False

    if(removed):

        return False

    if(reaction.emoji == symbols['back']):
        await response.cycleBackward()
        return True
    elif(reaction.emoji == symbols['forward']):
        await response.cycleForward()
        return True
    else:
        return False


menuCount = 0

async def MenuHandlerCallback(reaction, user, response, removed=False):
    global menuCount

    if(response.author.id != user.id):
        return False

    if(removed):
        if(reaction.emoji == symbols['menu']):
            menuCount -= 1
            if(menuCount == 0):
                await backend.emojiUnreact(response.response, symbols['img'])
                await backend.emojiUnreact(response.response, symbols['delete'])
        return False

    if(reaction.emoji == symbols['menu']):
        menuCount += 1

        if(menuCount > 0):
            await backend.emojiReact(response.response, symbols['img'])
            await backend.emojiReact(response.response, symbols['delete'])

        return False

    #elif(reaction.emoji == symbols['img']):
    elif(reaction.emoji == symbols['delete']):
        await backend.cleanupMessage(response.request)
        await backend.cleanupMessage(response.response)


    else:
        return False



async def addCycleHandler(response):
    add(response.response, CycleHandlerCallback, response)

    await backend.emojiReact(response.response, symbols['back'])
    await backend.emojiReact(response.response, symbols['forward'])


async def addMenuHandler(response, addEmoji=True):

    add(response.response, MenuHandlerCallback, response)

    if(addEmoji):
        await backend.emojiReact(response.response, symbols['menu'])

async def deleteMenuHandler(response, addEmoji=True):
    await backend.emojiUnreact(response.response, symbols['delete'])
