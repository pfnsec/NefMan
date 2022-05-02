#!/usr/bin/env python
from setuptools import setup

setup(
   name='nefman',
   version='0.1',
   description='A fairly useful Discord bot',
   author='Peter Sherman',
   author_email='pfnsec@gmail.com',
   packages=['nefman'],
   install_requires=[
      'requests', 
      'TinyDB',
      'fuzzywuzzy', 
      'google-api-python-client', 
      'oauth2client', 
      'discord', 
      'dateparser', 
      'pokebase', 
      'lxml', 
      'Pillow',
      'python-Levenshtein',
      'beautifulsoup4',
   ]
)
