import backend
import pipeline


import re
import traceback


commandlist = {}

class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)

class Request:
    def __init__(self, message):
        self.author  = message.author
        self.message = message
        #self.args    = re.split('\s*', message.content)[1:]
        self.args    = message.content.split()[1:]
        #print("Request(): ", self.args)
        #print(message.content.split())
        self.arg     = ' '.join(self.args)


async def command(message):
    m = re.match('\s*[%]([a-z0-9]+)(!?)\s*', message.content)
    if m is None: return

    cmd  = re.split('\s*', message.content)
    name = m.group(1)

    bang = m.group(2)

    req = Request(message)


    if name in commandlist:
        try:
            await commandlist[name](req)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            await backend.errorReact(req.message)
        #commandlist[name]([name] + cmd[1:])

pipeline.append(command)

def man(req):
    manpage = "```markdown\n"

    #To left-justify the command list, we 
    #take the longest command name and add 2 for formatting:
    maxlen = len(max(commandlist, key = len)) + 2

    for cmd in commandlist:
        entry = commandlist[cmd].__doc__
        if entry is None: continue
        cmd = f'%{cmd}:'.ljust(maxlen, ' ')
        manpage += f'{cmd}\t{entry}\n'

    manpage += "```"
    return manpage


#Insert a command into the list
def append(operator, names):
    if type(names) is not list: names = [names]

    for n in names:
        commandlist[n] = operator
