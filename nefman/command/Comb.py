
import command
import backend
import config
import message
import reaction

import re
import requests
import lxml
from lxml import html



url = config.require('co', 'url')
v_url = config.require('co', 'v_url')


url_search = f"https://{url}/a/q"
url_clip   = f"https://{url}/create-clip"


class CombResult():
    def __init__(self, media, ts1, ts2=None):
        self.media  = media
        self.ts1    = ts1
        self.ts2    = ts2
        self.length = 0


class CombResponse(message.Response):
    def __init__(self, results, request):
        #super().__init__(request, kind='image')
        super().__init__(request)
        self.results = results
        self.load()

    async def cycleForward(self):
        self.index = (self.index + 1) % len(self.results)
        self.load()
        await self.edit()

    async def cycleBackward(self):
        self.index = (self.index - 1) % len(self.results)
        self.load()
        await self.edit()


    def load(self):
        e = self.results[self.index]

        r = requests.get(f'https://{url}/timeline/{e.media}?ts1={e.ts1}')

        if not r.ok:
            #await backend.errorReact(req.message)
            print(r.reason)
            return

        clip_results = r.content.decode("utf-8")


        htmlElem = html.document_fromstring(clip_results)

        clips = htmlElem.cssselect("[name=ts2]")

        e.ts2 = clips[-2].items()[2][1]

        r = requests.post(url_clip,  data = {'media': str(e.media), 'ts1':str(e.ts1), 'ts2':str(e.ts2)})

        m = re.match(f'.*?"({v_url}/.*?)".?', r.content.decode("utf-8"))

        htmlElem = html.document_fromstring(r.content)

        clip = htmlElem.cssselect('[type="video/mp4"]')

        self.url = clip[0].items()[0][1]
        self.text = clip[0].items()[0][1]



async def search(req):
    f"""Search {url}"""

    r = requests.post(url_search,  data = {'q': req.arg})

    search_results = r.content.decode("utf-8")

    if not r.ok:
        await backend.errorReact(req.message)
        return

    htmlElem = html.fragments_fromstring(search_results)

    urls = re.findall(r'/timeline/\w+\?ts1=[0-9]+', r.content.decode("utf-8") )

    results = []

    for h in htmlElem[1:]:
        m = re.match('.*?/timeline/([a-zA-Z0-9]+)\?ts1=([0-9]+).*?', h.items()[1][1])

        media  = m.group(1)
        ts1    = int(m.group(2))
        ts2    = int(m.group(2)) + 10000

        results.append(CombResult(media, ts1))

    response = CombResponse(results, req.message)

    await backend.sendPackedResponse(response)

    await reaction.addCycleHandler(response)

command.append(search, 'co')
