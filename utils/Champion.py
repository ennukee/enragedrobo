import json
from discord.ext import commands	
import discord	
import urllib.request				
import requests	
from utils.BasicUtility import * # Basic utility functions
from utils.ResponseChecker import ResponseChecker

"""
League of Legends API non-command related methodology (keyword: Champion)

Contains various logic used in the commands located in `leagueapi.py`
"""

riot_base = "https://na.api.pvp.net"
params = dict(api_key=load_api_key('LoL'))

# - - - - - - - - - - - - - - - - - - - - - -  #
# - -          General use methods        - -  #
# - - - - - - - - - - - - - - - - - - - - - -  #

def champion_name_by_id(id):
	name = champion_stats_by_id(id)
	if(name):
		return name['id']
	else:
		return None

def champion_stats_by_name(name):
	"""Solely champion stats, no abilties"""
	data = load_champion_stats()
	try:
		return [data[x] for x in data if x.lower() == name.lower()]
	except KeyError as e:
		return None

def champion_stats_by_id(id):
	"""Solely champion stats, no abilties"""
	data = load_champion_stats()
	cdata = [data[x] for x in data if data[x]['key']==str(id)]
	if(cdata):
		return cdata[0]
	else:
		return None

def player_data(name, region='na'):
    """Find a player's ID by their summoner name"""
    url = riot_base + '/api/lol/{}/v1.4/summoner/by-name/{}'.format(region, name)
    resp = requests.get(url=url, params=params)
    if(ResponseChecker.is_good(resp.status_code)):
      data = json.loads(resp.text)[name.lower()]
      return data
    else:
      raise ValueError(ResponseChecker.meaning(resp.status_code))

def player_champion_data(p_id, region='na'):
  """Finds a player's champion data (level, mastery, etc) by their summoner ID"""
  url = riot_base + '/championmastery/location/{}1/player/{}/champions'.format(region.upper(), p_id)
  resp = requests.get(url=url, params=params)
  if(ResponseChecker.is_good(resp.status_code)):
    data = json.loads(resp.text)
    return data
  else:
    raise ValueError(ResponseChecker.meaning(resp.status_code))

# - - - - - - - - - - - - - - - - - - - - - -  #
# - -         Data loading methods        - -  #
# - - - - - - - - - - - - - - - - - - - - - -  #

def load_champion_stats(parsed=True):
	with open('data/league/champion.json') as f:
		return json.load(f)['data'] if parsed else json.load(f)

def load_realm_data(realm='na'):
	with open('data/league/{}.json'.format(realm)) as f:
		return json.load(f)

def load_champion_data(name):
	if name not in load_champion_stats():
		return
	with open('data/league/champions/{}.json'.format(name)) as f:
		return json.load(f)['data'][name]


# - - - - - - - - - - - - - - - - - - - - - -  #
# - -        Data refreshing methods      - -  #
# - - - - - - - - - - - - - - - - - - - - - -  #

def refresh_champion_data():
	refresh_realm_data() 			# Make sure version data is up to date for usage later on
	realm = load_realm_data()		# Load the refreshed realm data
	data = load_champion_stats()	# And get champion stats for the names

	names = [x for x in data]
	for name in names:
		try:
			url = 'http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion/{}.json'.format(realm['v'], name)
			urllib.request.urlretrieve(url, "data/league/champions/{}.json".format(name))
		except (ValueError, urllib.request.URLError) as e:
			raise e

def refresh_realm_data(realm='na'):
	try:
		url = 'https://ddragon.leagueoflegends.com/realms/{}.json'.format(realm)
		urllib.request.urlretrieve(url, 'data/league/{}.json'.format(realm))
	except (ValueError, urllib.request.URLError) as e:
		raise e
	
  