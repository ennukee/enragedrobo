# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import urllib.request # Downloading
import random # Random (RNG)

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils import imageloader # Image downloader
from utils.BasicUtility import *


class FunStuff:
  def __init__(self, bot):
    self.bot = bot

  @commands.command(pass_context=True, hidden=True)
  async def funnify(self, ctx, mode : int, word : str):
    print('funnify mode {} word {}'.format(mode, word))
    if mode == 1:
      m = ""
      for i in word:
        m += " "*random.randrange(1,10) + i + '\n'
      await self.bot.say(m)

    if mode == 2:
      m = ""
      for i in word:
        m += random.randrange(0,10)*i + '\n'
      await self.bot.say(m)
  
def setup(bot):
  bot.add_cog(FunStuff(bot))
