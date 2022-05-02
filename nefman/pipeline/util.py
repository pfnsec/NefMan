import backend
import pipeline

async def run(message):
    if message.content == '~':
        await backend.cleanupResponse(message)

    elif message.content == '!':
        await backend.cleanupRequest(message)

    elif message.content == '=':
        await backend.recycle(message)
        await backend.cleanupMessage(message)

    elif message.content == '>':
        await backend.cycleForward(message)
        await backend.cleanupMessage(message)

    elif message.content == '<':
        await backend.cycleBackward(message)
        await backend.cleanupMessage(message)

    elif message.content == '>>':
        await backend.cycleForward(message, delete=True)
        await backend.cleanupMessage(message)

    elif message.content == '<<':
        await backend.cycleBackward(message, delete=True)
        await backend.cleanupMessage(message)

pipeline.append(run)
