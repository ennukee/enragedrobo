# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import urllib.request # Downloading
import random # Random (RNG)
import datetime

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils import imageloader # Image downloader
from utils.BasicUtility import *
from utils.BotConstants import *


class Misc:
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def uptime(self):
    """Current uptime of the bot"""
    current_time = datetime.datetime.now()
    diff = current_time - botv.get_start()

    out = []
    if diff.days > 0:
      out.append("{} day(s)".format(diff.days))
    if diff.seconds > 3600:
      hours = int(diff.seconds / 3600)
      out.append("{} hour(s)".format(hours))
    if diff.seconds > 60:
      minutes = int(diff.seconds / 60) % 60
      if minutes > 0:
        out.append("{} minute(s)".format(minutes))
    seconds = diff.seconds % 60
    if seconds > 0:
      out.append("{} second(s)".format(seconds))

    await self.bot.say(', '.join(out))
      
def setup(bot):
  bot.add_cog(Misc(bot))
