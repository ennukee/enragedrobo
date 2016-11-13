# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import datetime, re # Datetime and regular expression libraries
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import requests # API queries
import urllib.request # Downloading
import random # Random (RNG)
import textwrap

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils.ResponseChecker import ResponseChecker # Checks HTTP response codes
from utils.QueueType import QueueType # Converts queue IDs to names
from utils.MapNames import MapNames # Converts map IDs to names
from utils.Champion import * # Various champion data related operations
from utils.BasicUtility import * # Basic utility functions

import checks # Ensures various predefined conditions are met

# - - - - - - - - - - - - - - - - - - - - - - #
# - - League of Legends API Usage section - - #
#      Base URL: https://na.api.pvp.net/      #
# - - - - - - - - - - - - - - - - - - - - - - #

class LeagueAPI:
  def __init__(self, bot):
    self.bot = bot
    self.riot_base = "https://na.api.pvp.net"
    self.params = dict(api_key=load_api_key('LoL'))

  @commands.command(pass_context=True)
  async def player(self, ctx, name : str, show_id=False):
    """League of Legends player data (do not include spaces in names)"""
    # TODO: Incomplete (use other API queries to improve this)
    try:
      data = player_data(name)
      c_data = player_champion_data(data['id'])
    except ValueError as e:
      await self.bot.say(str(e))
      raise e
      return

    def int_to_date(i):
      proper = i / 1e3
      dtv = datetime.datetime.fromtimestamp(proper) # datetime value
      return "{}/{}/{}".format(dtv.month, dtv.day, dtv.year)

    S_count = 0
    for champ in c_data:
      try:
        if champ['highestGrade'] in ['S-','S','S+']:
          S_count += 1
      except Exception as e:
        pass
    p_id = data['id']
    msg = []
    msg.append(
      """\
      **Username**: {}{}
      **Level**: {}
      """.format(data['name'], "\n        **ID**: {}".format(p_id) if show_id else "", data['summonerLevel'])
      )
    msg.append(
      """\
      **Most played champions**\
      """
      )
    for i in range(0,3):
      try:
        max_rank = c_data[i]['highestGrade']
      except Exception as e:
        max_rank = "N/A"
      msg.append(
        """\
        {}. **{}** (Best: **{}**) *(Last played: {})*\
        """.format(i+1, champion_name_by_id(c_data[i]['championId']), max_rank, int_to_date(c_data[i]['lastPlayTime']))
        )
    msg.append("")
    msg.append(
      """\
      Total S count (S- or higher): {} of {}\
      """.format(S_count, len(load_champion_stats()))
      )

    await self.bot.say(textwrap.dedent('\n'.join(msg)))

def setup(bot):
  bot.add_cog(LeagueAPI(bot))
