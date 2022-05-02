import os
import json
import sys

config = {}

directory = './config'

for file in os.listdir(directory):
    if file.endswith(".json"):
        section = os.path.splitext(file)[0]

        with open(os.path.join(directory, file)) as json_data:
            config[section] = json.load(json_data)
    else:
        continue

def lookup(section, key):
    if section in config:
        if key in config[section]:
            return config[section][key]
        else:
            return False
    else:
        return False

def require(section, key):
    if section in config:
        if key in config[section]:
            return config[section][key]
        else:
            sys.exit(f'Error: Missing required config parameter {key} in file {directory}/{section}.json! Add this parameter to continue.')
    else:
        sys.exit(f'Error: Missing required config file {directory}/{section}.json! Create this file and add parameter {key} to continue.')
