import os, glob
import pprint
import backend



pipelinelist = []


def append(operator):
    pipelinelist.append(operator)

async def run(message):
    for fn in pipelinelist:
        await fn(message)
