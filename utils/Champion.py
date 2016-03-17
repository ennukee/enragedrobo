import json
from discord.ext import commands	
import discord	
import urllib.request					

# - - - - - - - - - - - - - - - - - - - - - -  #
# - -          General use methods        - -  #
# - - - - - - - - - - - - - - - - - - - - - -  #

def champion_name_by_id(id):
	name = champion_data_by_id(id)
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
	