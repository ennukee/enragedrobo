import json
import os

def load_api_key(name):
  with open('data/apikeys.json') as f:
    try:
      return json.load(f)[name]
    except KeyError as e:
      return None

def load_credentials():
  with open('data/login.json') as f:
    return json.load(f)

def admins():
  with open('data/admins.json') as f:
    j = json.load(f)
    return [x for x in j if j[x]==1]

def custom_command_list():
  return [x[:-5] for x in os.listdir('./data/custom_commands')]

def clean(i):
  return i.lower().replace(' ','')



