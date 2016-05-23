# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import urllib.request # Downloading
import random # Random (RNG)
from datetime import datetime

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

  @commands.command(pass_context=True)
  async def timeuntil(self, ctx, time : str, format = '%m/%d/%Y@%I%p'):

    def logic(time):
      time_until = time - datetime.now()
      numerics = {
                  'days': time_until.days,
                  'hours': (time_until.seconds / (60 * 60)) % 24, 
                  'minutes': (time_until.seconds / 60) % 60, 
                  'seconds': time_until.seconds % 60
                  }
      output = ""
      for i in ['days', 'hours', 'minutes', 'seconds']:
        if numerics[i] >= 1:
          output += "{} {} ".format(int(numerics[i]), i)
      return output

    try:
      date_obj = datetime.strptime(time, format)
      await self.bot.say(logic(date_obj))
    except ValueError as e:
      try:
        with open('./data/time_keywords.json') as f:
          data = json.load(f)
          date_obj = datetime.strptime(data[time.lower()], format)
          await self.bot.say(logic(date_obj))
      except KeyError as e:
        await self.bot.say('The time provided did match the time format (`{}`)\n\nSee https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior for more information'.format(format))
      except Exception as e:
        await self.bot.say('Something went wrong!\n\n`{}: {}`'.format(type(e).__name__, e))   
  
def setup(bot):
  bot.add_cog(FunStuff(bot))
