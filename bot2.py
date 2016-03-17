# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord	# Overall discord library
import datetime, re # Datetime and regular expression libraries
import json, asyncio # json / asyncio libraries
import copy
import logging # Debug logging
import sys, os # Lower-level operations libraries
import requests # API queries
import textwrap 
import urllib.request # Downloading
import random # Random (RNG)
from time import sleep # For delays
from collections import defaultdict 
import numpy as np # Advanced number/set arithmetic

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils import imageloader # Image downloader


# - - - - - - - - - - #
# - - Setup stuff - - #
# - - - - - - - - - - #

# - - Bot data - - #
description = """
Hey there, I'm enragedrobo. A bot designed by Dylan (aka enragednuke) to provide convenient utilities.
"""

initial_extensions = [
	'modules.trivia',
	'modules.leagueapi',
	'modules.botconfig'
]

# - - Logger information - - #
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# - - Bot instantiation - - #
bot = commands.Bot(command_prefix=[';'], description=description, pm_help=None, help_attrs=dict(hidden=True))

# - - Game constants - - #
from utils.BotConstants import *


# - - - - - - - - - - - - - - - - - - - - - -  #
# - - Bot commands / generic library usage - - #
# - - - - - - - - - - - - - - - - - - - - - -  #

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	await bot.change_status(game=discord.Game(name="Half Life 3"))
	for extension in initial_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

@bot.event
async def on_message(message):
	if message.author.id == botv.id:
		return

	if bot.user in message.mentions or bot.user.name.lower() in message.content.lower():
		await bot.send_message(message.channel, "I\'m a bot! If you're trying to talk to me, you probably mean to talk to my creator <@126122455248011265>")
	if not message.attachments and message.content[0] in bot.command_prefix:
		if message.content[1:] in custom_command_list():
			with open('data/custom_commands/{}.json'.format(message.content[1:])) as f:
				data = json.load(f)
				try:
					output = eval(data['content']) if data['code'] else data['code']
				except Exception as e:
					await bot.send_message(message.channel, '```py\n{}\n```'.format(type(e).__name__ + ': ' + str(e)))
					return
				if asyncio.iscoroutine(output):
					output = await output
				if data['output']:
					await bot.send_message(message.channel, output)
	await bot.process_commands(message)

@bot.event
async def on_member_update(before, after):
	"""Have the bot mimic your game (but reversed) whenever you enter a game, then reset after you leave said game"""
	if(before.id == '126122455248011265'): 
		if(before.game != after.game):
			if(after.game == None):
				await bot.change_status(game=discord.Game(name=random.choice(['Half Life 3','with your mother','Meme Simulator 2k16','Portal 3'])))
			else:
				await bot.change_status(game=discord.Game(name=after.game.name[::-1]))

@bot.command(hidden=True)
@checks.is_admin()
async def refresh(*names : str):
	if 'realm' in names:
		try:
			refresh_realm_data()
			await bot.say("Successfully reloaded realm data")
		except (ValueError, urllib.request.URLError) as e:
			await bot.say("There was an error loading data (admin: see console)")
			print(e)
	if 'champion' in names:
		try:
			refresh_champion_data()
			await bot.say("Successfully reloaded champion data")
		except (ValueError, urllib.request.URLError) as e:
			await bot.say("There was an error loading data (admin: see console)")
			print(e)
	if(len(names) == 0):
		try:
			refresh_champion_data()
			refresh_realm_data()
			await bot.say("Successfully reloaded all data")
		except (ValueError, urllib.request.URLError) as e:
			await bot.say("There was an error loading data (admin: see console)")
			print(e)

@bot.command(pass_context=True, hidden=True)
async def avatar(ctx, *name : str):
	"""Retrieve a larger version of any users' avatar."""
	user = ' '.join(name)
	for msg in ["**{0}**'s avatar: {1}".format(x.name, x.avatar_url) if x.name.lower()==user.lower() else None for x in ctx.message.server.members]:
		if msg != None:
			await bot.say(msg)
			return
	await bot.say("Invalid name")


# - - - - - - - - - - - - - - - - - - - - - - - - - - -  #
# - - Beginning of utility section (non-api related) - - #
# - - - - - - - - - - - - - - - - - - - - - - - - - - -  #

def load_credentials():
	with open('data/login.json') as f:
		return json.load(f)

def load_api_key(name):
	with open('data/apikeys.json') as f:
		try:
			return json.load(f)[name]
		except KeyError as e:
			return None

def admins():
	with open('data/admins.json') as f:
		j = json.load(f)
		return [x for x in j if j[x]==1]

def custom_command_list():
	return [x[:-5] for x in os.listdir('./data/custom_commands')]

# - - Program run section - - #

if __name__ == '__main__':
	if any('debug' in arg.lower() for arg in sys.argv):
		bot.command_prefix = '$'

	login = load_credentials()
	bot.run(login['email'], login['password'])