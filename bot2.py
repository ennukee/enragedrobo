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
from _thread import *
from bs4 import BeautifulSoup

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils import imageloader # Image downloader
from utils.Champion import *
from utils.BasicUtility import * # Basic utility functions
from utils.MALutil import * # MyAnimeList utility functions


# - - - - - - - - - - #
# - - Setup stuff - - #
# - - - - - - - - - - #

# - - Bot data - - #
description = """
Hey there, I'm enragedrobo. A bot designed by Dylan (aka enragednuke) to provide convenient utilities.
"""

# - - Logger information - - #
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# - - Bot instantiation - - #
bot = commands.Bot(command_prefix=['?'], description=description, pm_help=None, help_attrs=dict(hidden=True))

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
  for extension in botv.initial_extensions:
    try:
      bot.load_extension(extension)
    except Exception as e:
      print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

@bot.event
async def on_message(message):
  # IDs
  author_id, server_id, channel_id = message.author.id, message.server.id, message.channel.id

  if author_id == bot.user.id:
    return

  swi_path = './data/command_ignores/servers/{}/'.format(server_id)
  ci_path = './data/command_ignores/channels/{}/'.format(channel_id)

  if not os.path.exists(swi_path):
    os.makedirs(swi_path)
  if not os.path.exists(ci_path):
    os.makedirs(ci_path)

  def extract_word(word):
    if not word or word[0] != bot.command_prefix[0]:
      return ''
    return word.split()[0][1:]

  invoker = extract_word(message.content)
  server_wide_ignored = [f for f in os.listdir(swi_path)]
  channel_ignored = [f for f in os.listdir(ci_path)]
  ignored = server_wide_ignored + channel_ignored

  print(invoker)
  print(server_wide_ignored)
  print(channel_ignored)

  if invoker in ignored:
    return

  auto_responses = {
    "ayy": "lmao",
    "o shit": "wadup",
    "its": "dat boi",
    u"(╯°□°）╯︵ ┻━┻": u"#tablelivesmatter\n┬─┬﻿ ノ( ゜-゜ノ)",
    "\\o\\": "/o/"
    }
  if message.content in auto_responses.keys():
    await bot.send_message(message.channel, auto_responses[message.content])

  if message.content.startswith('BUG') and message.channel.is_private:
    bug_report = '<@{}>\nBug report by <@{}>: {}'
    await bot.send_message(discord.Object(botv.bug_reports_channel_id), bug_report.format(botv.owner_id, message.author.id, message.content[3:]))

  for user in list(set(message.mentions)): # removes duplicates
    if botv.is_afk(user):
      await bot.send_message(message.channel, "**{}** is AFK\n\nReason provided\n**{}**".format(user.name, botv.afk_reason(user)))

    # MYANIMELIST MANGA AND ANIME SEARCH CODE #

  if not 'anime' in ignored:
    # Link anime details by link #
    animes = [x[0] for x in re.findall("\<(http://(www\.)?myanimelist.net/anime/\d+/?[A-Za-z\_\-(%20)]*)\>", message.content)]
    end = []
    for anime in animes[0:3]:
      end.append('\n'.join(MAL_anime_info(anime)))
    if end:
      await bot.send_message(message.channel, '\n\n'.join(end))

    search_error = "There was an issue searching **{}**. It\'s likely that the title contains characters not supported by Discord/Python\'s basic text engine\n\nIf this is not the case, please send this bot a message starting with `BUG ` and report the issue! Thanks!"
    # Link anime details by search query #
    anime_search = re.findall('\<([\w\s^(http|www)]*)\>', message.content)
    end = [] # resetting old array
    for ani_s in anime_search[0:3]:
      print(ani_s)
      try:
        result = MAL_anime_search(ani_s)
        end.append('\n'.join(MAL_anime_info(result.get('href'))))
      except Exception as e:
        await bot.send_message(message.channel, search_error.format(ani_s))
        continue
    if end:
      await bot.send_message(message.channel, '\n'.join(end))

  if not 'manga' in ignored:
    # Link manga details by link #
    mangas = [x[0] for x in re.findall("\<(http://(www\.)?myanimelist.net/manga/\d+/?[A-Za-z\_\-(%20)]*)\>", message.content)]
    end = []
    for manga in mangas[0:3]:
      end.append('\n'.join(MAL_manga_info(manga)))
    if end:
      await bot.send_message(message.channel, '\n\n'.join(end))

    # Link manga details by search query #
    manga_search = re.findall('\[([\w\s^(http|www)]*)\]', message.content)
    end = [] # resetting old array
    for mang_s in manga_search[0:3]:
      print(mang_s)
      try:
        result = MAL_manga_search(mang_s)
        end.append('\n'.join(MAL_manga_info(result.get('href'))))
      except Exception as e:
        await bot.send_message(message.channel, search_error.format(mang_s))
        continue
    if end:
      await bot.send_message(message.channel, '\n'.join(end))

  await bot.process_commands(message)

@bot.event
async def on_member_update(before, after):
  """Have the bot mimic your game (but reversed) whenever you enter a game, then reset after you leave said game"""
  if(before.id == '126122455248011265'):
    if(before.game != after.game):
      if(after.game == None):
        await bot.change_status(game=discord.Game(name=random.choice(['Half Life 3','Portal 3'])))
      else:
        await bot.change_status(game=discord.Game(name=after.game.name[::-1]))

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
@checks.not_private()
@checks.is_owner()
async def announce(ctx, role : str, *message : str):
  """Create a message that mentions everyone in a role with a specified message.

  Mainly unused now that Discord implemented role-mentions.

  Currently not multi-server supported. Due to natural Discord implemention, this is likely to be removed in the near future.
  """
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
@checks.not_private()
@checks.is_owner()
async def survey(ctx, role : str, *question : str):
  """Send a survey to everyone of a specified role.

  Currently not multi-server supported, aimed as a rework project in the future.
  """
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
@checks.not_private()
async def commands(ctx):
  """Returns a full list of commands (sends you a PM)

  Can only be used from a server. Does not work in private messages."""
  server_id = ctx.message.server.id
  server_cmd_dir = './data/custom_commands/{}'.format(server_id)

  base_commands = "**For a full list of the global commands** the bot has to offer, please visit the bot's official website: http://enragednuke.github.io/enragedrobo/\n"

  custom_commands = "**Server commands** (for the server you messaged from)\n\n"
  if os.path.isdir(server_cmd_dir) and len(os.listdir(server_cmd_dir))>0:
    for cmd in os.listdir(server_cmd_dir):
      custom_commands += "`{}`\n".format(cmd[:-5])
  else:
    custom_commands += "Your server has no commands!"

  await bot.send_message(ctx.message.author, '\n'.join([base_commands, custom_commands]))

# - - Program run section - - #

if __name__ == '__main__':
  if any('debug' in arg.lower() for arg in sys.argv):
    bot.command_prefix = '$'

  login = load_credentials()
  bot.run(login['token'])