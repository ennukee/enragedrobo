# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord  # Overall discord library
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
from utils.Champion import *
from utils.BasicUtility import * # Basic utility functions


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
  'modules.botconfig',
    'modules.funstuff'
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
        print(data['code'])
        try:
          output = eval(data['content']) if data['code'] else data['content']
        except Exception as e:
          await bot.send_message(message.channel, '```py\n{}\n```'.format(type(e).__name__ + ': ' + str(e)))
          return
        if asyncio.iscoroutine(output):
          output = await output
        if data['output']:
          await bot.send_message(message.channel, output)
  await bot.process_commands(message)

@bot.event
async def on_voice_state_update(before, after):
  if after.voice_channel and before.voice_channel != after.voice_channel:
    if botv.private_channel and after.voice_channel == botv.private_channel[1]:
      await bot.move_member(after, after.server.afk_channel)
      await bot.send_message(after, 'You cannot join this channel while it is locked! (locked by **{}**)'.format(botv.private_channel[0]))

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
@checks.is_owner()
async def evalc(ctx, *, code : str):
    """Evaluates python code"""
    code = code.strip('` ')
    python = '```py\n{}\n```'
    result = None
    try:
        result = eval(code)
    except Exception as e:
        await bot.say(python.format(type(e).__name__ + ': ' + str(e)))
        return

    if asyncio.iscoroutine(result):
        result = await result
    await bot.say(python.format(result))

@bot.command(pass_context=True, hidden=True)
@checks.is_admin()
async def announce(ctx, role : str, *message : str):
  msg = ' '.join(message)

  role = discord.utils.find(lambda m : clean(m.name) == clean(role), ctx.message.server.roles)
  if role is None:
    await bot.say("That role does not exist")
    return

  people_with_role = [person for person in ctx.message.server.members if role in person.roles]
  send = ""
  for person in people_with_role:
    send += "<@{}> ".format(person.id)
  send += "\n{}".format(msg)
  await bot.say(send)

@bot.command(pass_context=True, hidden=True)
@checks.is_admin()
async def survey(ctx, role : str, *question : str):
  msg = ' '.join(question)

  role = discord.utils.find(lambda m : clean(m.name) == clean(role if role is not 'everyone' else '@everyone'), ctx.message.server.roles)
  if role is None:
    await bot.say("That role does not exist")
    return

  people_with_role = [person for person in ctx.message.server.members if role in person.roles and person.status != discord.Status.offline]
  responses = {}

  await bot.say("Survey started. It will send to one person at a time, so be patient.")

  for person in people_with_role:
    if person.bot:
      print("The user {} is a bot user. Skipping.".format(person.name.encode('utf-8')))
      continue
    survey = """\
      {} has sent a survey. You have two minutes to reply with your response.
      (Do not try to use multiple responses, it will only record the first thing you say. Use shift+enter to have multiple lines)

      **Question**: {}
      """
    print('Sending message to {}'.format(person.name.encode('utf-8')))
    await bot.send_message(person, survey.format(ctx.message.author, msg))
    response = await bot.wait_for_message(timeout=120.0, author=person)
    print('Response received from {}'.format(person.name.encode('utf-8')))

    if response is None:
      responses[person.name] = 'No response'
      await bot.send_message(person, "You took too long, so your chance to reply has ended. Thank you anyway.")
    else:
      responses[person.name] = response.content
      await bot.send_message(person, "Response received, thank you")

  await bot.say("Survey completed")

  result = """\
    Survey completed.

    **Results**
    {}
    """
  response_list = ""
  for response in responses:
    response_list += "**{}**: {}\n".format(response, responses[response])
  await bot.send_message(ctx.message.author, result.format(response_list))

@bot.command(pass_context=True)
async def avatar(ctx, *name : str):
  """Retrieve a larger version of any users' avatar."""
  user = ' '.join(name)
  for msg in ["**{0}**'s avatar: {1}".format(x.name, x.avatar_url) if x.name.lower()==user.lower() else None for x in ctx.message.server.members]:
    if msg != None:
      await bot.say(msg)
      return
  await bot.say("Invalid name")

@bot.command(pass_context=True)
async def commands(ctx):
  """Returns a full list of commands (sends you a PM)"""
  def rip_perm_name(i):
    if len(i)==0:
      return ["all", ""]
    else:
      role = str(i[0]).split()[1].split('.')[0].split('_')[1]
      return (role, "(**{0}** only)".format(role))

  def print_table(table, forw):
    to_return = "**{} commands**\n\n".format(forw)
    c1w = max([len(x) for x in table.keys()])
    c2w = max([len(x) for x in table.values()])
    for k,v in table.items():
      to_return += "`{0:<{col1}} {1:<{col2}}`\n".format(k,v,col1=c1w, col2=c2w)
    return to_return

  index = {'all':{}, 'admin':{}, 'owner':{}}
  for (name,command) in bot.commands.items():
    params = [x for x in command.params if x not in ['self','ctx']]
    restriction = rip_perm_name(command.checks)
    print(restriction)
    index[restriction[0]][name] = ('<' + '> <'.join(params) + '>' if len(params)>0 else '')

  custom_commands = "**Custom commands** (for everyone)\n\n"
  for cmd in os.listdir('./data/custom_commands'):
    custom_commands += "`{}`\n".format(cmd[:-5])

  print(index)
  await bot.send_message(ctx.message.author, '\n'.join( (print_table(index['owner'], 'Owner'), print_table(index['admin'], 'Admin'), print_table(index['all'], 'Everyone\'s'), custom_commands) ))

@bot.command(hidden=True)
@checks.is_admin()
async def load(name : str):
  possible = ['music']
  if name.lower() not in possible:
    await bot.say("That is not a loadable file")
    return
  else:
    if name.lower() == 'music':
      await bot.say("Loading music bot (note: this method makes the normal bot operations unusable until ;end is called)")
      os.system("py bot2_music.py")

# - - Program run section - - #

if __name__ == '__main__':
  if any('debug' in arg.lower() for arg in sys.argv):
    bot.command_prefix = '$'

  login = load_credentials()
  #bot.client_id = login['client_id']
  bot.run(login['token'])