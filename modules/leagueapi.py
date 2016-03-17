# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import datetime, re # Datetime and regular expression libraries
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import requests # API queries
import urllib.request # Downloading
import random # Random (RNG)

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils.ResponseChecker import ResponseChecker # Checks HTTP response codes
from utils.QueueType import QueueType # Converts queue IDs to names
from utils.MapNames import MapNames # Converts map IDs to names
from utils.Champion import * # Various champion data related operations

# - - - - - - - - - - - - - - - - - - - - - - #
# - - League of Legends API Usage section - - #
#      Base URL: https://na.api.pvp.net/      #
# - - - - - - - - - - - - - - - - - - - - - - #

class LeagueAPI:
  def __init__(self, bot):
    self.bot = bot
    self.riot_base = "https://na.api.pvp.net"

  @commands.command()
  async def player(self, name : str):
    """League of Legends player data"""
    # TODO: Incomplete (use other API queries to improve this)
    url = self.riot_base + '/api/lol/na/v1.4/summoner/by-name/{0}'.format(name)
    params = dict(
      api_key=load_api_key('LoL')
    )
    resp = requests.get(url=url, params=params)
    if(ResponseChecker.is_good(resp.status_code)):
      data = json.loads(resp.text)[name]
      msg = """\
          **Username**: {0}
          **ID**: {1}
          **Level**: {2}""".format(data['name'], data['id'], data['summonerLevel'])
      await self.bot.say(textwrap.dedent(msg))
    else:
      await self.bot.say(ResponseChecker.meaning(resp.status_code))

  @commands.command()
  async def champion(self, name : str):
    """League of Legends champion data"""
    # TODO: Incomplete
    name = name.replace('\'','')
    data = champion_stats_by_name(name.capitalize())
    if(data):
      # parse data
      await self.bot.say(data)
    else:
      await self.bot.say("That is not a valid champion name\n(Note: do not include spaces)")

def setup(bot):
  bot.add_cog(LeagueAPI(bot))