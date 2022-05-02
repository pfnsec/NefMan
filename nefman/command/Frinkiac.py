import base64, requests
import message
import backend
import command
import reaction



global url_meme
global url_search
global url_caption
url_meme    = 'https://frinkiac.com/meme'
url_search  = 'https://frinkiac.com/api/search'
url_caption = 'https://frinkiac.com/api/caption'
proxies = {}

class FrinkiacResponse(message.Response):
    def __init__(self, results, request):
        super().__init__(request, kind='image')
        self.results = results
        self.loadFrinkiac()

    async def cycleForward(self):
        self.index = (self.index + 1) % len(self.results)
        self.loadFrinkiac()
        await self.edit()

    async def cycleBackward(self):
        self.index = (self.index - 1) % len(self.results)
        self.loadFrinkiac()
        await self.edit()


    def loadFrinkiac(self):
        r = self.results[self.index]

        episode = r['Episode']
        timestamp = r['Timestamp']

        caption   = get_caption(self.request, episode, timestamp)
        subtitles = '\n'.join(s['Content'] for s in caption['Subtitles'])

        self.url = f'{url_meme}/{episode}/{timestamp}'
        self.text = subtitles


def get_search(message, quote):
    r = requests.get(url_search, proxies = proxies, params = {'q': quote})
    if not r.ok:
        backend.errorReact(message)
        raise RuntimeError(f'{r.status_code} - {r.reason} - {r.text}')
    return r.json()

def get_caption(message, episode, timestamp):
    r = requests.get(url_caption, proxies = proxies, params = {'e': episode, 't': timestamp})
    if not r.ok:
        backend.errorReact(message)
        raise RuntimeError(f'{r.status_code} - {r.reason} - {r.text}')
    return r.json()

def get_meme(message, episode, timestamp, quote):
    quote = base64.b64encode(quote.encode(), b'+_')
    r = requests.get(f'{url_meme}/{episode}/{timestamp}', proxies = proxies, params = {'b64lines': quote})
    if not r.ok:
        backend.errorReact(message)
        raise RuntimeError(f'{r.status_code} - {r.reason} - {r.text}')
    return r.content

def set_url(url):
    global url_meme
    global url_search
    global url_caption
    url_meme    = f'https://{url}.com/meme'
    url_search  = f'https://{url}.com/api/search'
    url_caption = f'https://{url}.com/api/caption'

async def search(url, req):
    query = req.arg
    if query is "": return

    set_url(url)

    results = get_search(req.message, query)

    if len(results) is 0:
        await backend.errorReact(req.message)
        return

    response = FrinkiacResponse(results, req.message)

    await backend.sendPackedResponse(response)

    await reaction.addCycleHandler(response)
    #await backend.sendResponse(req.message, type='image', text = text_list, url = url_list)

async def Frinkiac(req):
    """Quote The Simpsons"""
    await search('frinkiac', req)

async def Morbotron(req):
    """Quote Futurama"""
    await search('morbotron', req)


command.append(Frinkiac,  ['fr'])
command.append(Morbotron, ['mo'])
