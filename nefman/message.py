
import config
import discord
import backend

import random

random.seed()

#Define a class to represent responses from commands.
#This facilitates deleting a response some time later,
#as well as cycling through a list of returned results
#by editing the message after the fact.

class Response:
    def __init__(self, request, text='', kind='text', url=None, fp=None, index=0):
        #The message this is responding to
        self.request = request
        self.author  = request.author
        self.channel = request.channel

        self.kind = kind
        self.fp = fp

        self.index = index

        if type(text) is list:
            self.text  = text[index]
            self.text_list = text
        else:
            self.text = text
            self.text_list = None

        if type(url) is list:
            self.url      = url[index]
            self.url_list = url
        else:
            self.url = url
            self.url_list = None


    async def delete(self):
        await backend.cleanupMessage(self.response)

    async def send(self):
        if(self.kind == 'text'):
            if self.url is not None:
                self.response = await backend.sendMessage(self.request.channel, self.url)
            else:
                self.response = await backend.sendMessage(self.request.channel, self.text)
        elif(self.kind == 'image'):
            em = discord.Embed(description=self.text, colour=self.request.author.colour)
            em.set_image(url=self.url)
            self.response = await backend.sendMessage(self.request.channel, "", embed=em)
        elif(self.kind == 'file'):
            #self.response = await backend.sendFile(self.request.channel, self.fp, filename=self.url)
            self.response = await backend.sendFile(self.request.channel, self.fp, filename=self.url, content=self.text)


    async def edit(self):
        print("self.edit", self)
        if(self.kind == 'text'):
            if self.url is not None:
                self.response = await backend.editMessage(self.response, self.url)
            else:
                self.response = await backend.editMessage(self.response, self.text)
        elif(self.kind == 'image'):
            em = discord.Embed(description=self.text, colour=self.request.author.colour)
            em.set_image(url=self.url)
            print('Image edit: ', self.url)
            self.response = await backend.editMessage(self.response, "", embed=em)
        else:
            if self.url is not None:
                self.response = await backend.editMessage(self.response, self.url)
            else:
                self.response = await backend.editMessage(self.response, self.text)

    async def recycle(self):
        await self.cycle()

    async def cycleForward(self):
        self.index = (self.index + 1) % len(self.url_list)
        await self.cycle()

    async def cycleBackward(self):
        self.index = (self.index - 1) % len(self.url_list)
        await self.cycle()

    async def cycle(self):
        print("cycle", self)
        if self.url_list is None and self.text_list is None:
            pass

        if self.url_list is not None:
            self.url = self.url_list[self.index]
        if self.text_list is not None:
            self.text = self.text_list[self.index]

        await self.edit()

    #select a random element
    async def shuffle(self):
        if self.url_list is None:
            return

        self.index = random.randrange(0, len(self.url_list))

        await self.cycle()





#For every user in every channel, we have a stack of responses that might be
#popped if they're deleted by a cleanup function.
#The stack is limited in length, and older entries will be deleted
#to make room. It's assumed that no user would ever trigger more than
#30 commands and then delete all of them (more than that just silently
#bugs out).


class History():
    def __init__(self):
        self.items = {}
        self.limit = int(config.lookup('discord', 'history_size')) or 30

    def push(self, message):
        author  = message.author
        channel = message.channel

        if not channel in self.items:
            self.items[channel] = {}

        if not author in self.items[channel]:
            self.items[channel][author] = []

        if not 'global' in self.items[channel]:
            self.items[channel]['global'] = []

        #Remove the head if we've hit the history limit
        if(len(self.items[channel][author]) == self.limit):
            self.items[channel][author].pop(0)

        self.items[channel][author].append(message)
        self.items[channel]['global'].append(message)

    def top(self, message):
        author  = message.author
        channel = message.channel

        if not channel in self.items:
            return None
        elif self.items[channel] == {}:
            return None
        elif self.items[channel][author] == []:
            return None
        else:
            return self.items[channel][author][-1]

    def global_top(self, message):
        author  = message.author
        channel = message.channel

        if not channel in self.items:
            return None
        elif self.items[channel] == {}:
            return None
        elif self.items[channel]['global'] == []:
            return None
        else:
            return self.items[channel]['global'][-1]

    def pop(self, message):
        author  = message.author
        channel = message.channel

        if not channel in self.items:
            return None
        elif self.items[channel] == {}:
            return None
        elif self.items[channel][author] == []:
            return None
        else:
            return self.items[channel][author].pop()
