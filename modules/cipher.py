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
from utils.BotConstants import *


class Cipher:
  """A work-in-progress side-project I'm doing for fun

  Aiming to have tons of different ciphers with their respective encrypters and decrypters. 

  Why? Why not.
  """
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def encrypt(self, *args):
    print('encrypt called w: {}'.format(args))
    if len(args) < 2 or args[1].lower() == 'caeser':
      caeser_out = '*Caeser* Cipher\n\n**Result**: {}\n**Shift**: {}'
      try:
        shift = int(args[2])
      except (ValueError,IndexError) as e:
        # Second argument is not a number or does not exist
        shift = random.randint(1,26)
      result_a = []
      for char in args[0]:
        new_ord = ord(char) + shift
        if new_ord > 126:
          new_ord -= 94
        result_a.append(chr(new_ord))
      result_s = ''.join(result_a)
      await self.bot.say(caeser_out.format(result_s, shift))
      
def setup(bot):
  bot.add_cog(Cipher(bot))
