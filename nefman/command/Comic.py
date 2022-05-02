import datetime
import command 
import backend
import config
import requests
from bs4 import BeautifulSoup


async def cah(req):
    """Get a random Calvin & Hobbes strip"""
    url = "https://www.gocomics.com/random/calvinandhobbes"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    comic = soup.findAll("div", {"class": "container"})
    url = comic[0]['data-image']
    
    resp = await backend.sendResponse(req.message, url)

    await resp.request.add_reaction('🐅')

command.append(cah, ["cah", "calvin"])