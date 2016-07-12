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


class DBD:
  def __init__(self, bot):
    self.bot = bot

  @commands.command(pass_context=True)
  async def hatch(self, ctx, map_name : str, zone_name : str):
    valid_maps = ['aw','me','cf']
    map_translations = {'aw': 'Autohaven Wreckers', 'me': 'MacMillan Estate', 'cf': 'Coldwind Farm'}
    valid_zones = {'aw': ['arp','bl','ws','wy'], 'me': ['ct','iom','sp','sw'], 'cf': ['ra','rf','tc','th']}
    zone_translations = {
                        'aw': {
                            'arp': 'Azarov\'s Resting Place',
                            'bl': 'Blood Lodge',
                            'ws': 'Wretched Shop',
                            'wy': 'Wreckers Yard'
                          },
                        'me': {
                            'ct': 'Coal Tower',
                            'iom': 'Ironworks Of Misery',
                            'sp': 'Suffocation Pit',
                            'sw': 'Shelter Woods'
                          },
                        'cf': {
                            'ra': 'Rancid Abattoir',
                            'rf': 'Rotten Fields',
                            'tc': 'Torment Creek',
                            'th': 'Thompson House'
                          }
                        }

    map_name = map_name.lower()
    zone_name = zone_name.lower()

    print('{} {}'.format(map_name, zone_name))
    if map_name in valid_maps:
      if zone_name in valid_zones[map_name]:
        image_path = './data/deadbydaylight/{}_{}.jpg'.format(map_name.upper(), zone_name.upper())
        text_path = './data/deadbydaylight/{}_{}.txt'.format(map_name.upper(), zone_name.upper())
        if os.path.isfile(image_path):
          await self.bot.send_file(ctx.message.channel, image_path)
        with open(text_path) as f:
          await self.bot.say(f.read())
      else:
        sup_zones = ["**{}** ({})".format(zone_n, zone_translations[map_name][zone_n]) for zone_n in valid_zones[map_name]]
        await self.bot.say('Supported zones for **{}**: {}'.format(map_name, ', '.join(sup_zones)))
    else:
      sup_maps = ["**{}** ({})".format(map_n, map_translations[map_n]) for map_n in valid_maps]
      await self.bot.say('Supported maps: {}'.format(', '.join(sup_maps)))

  
def setup(bot):
  bot.add_cog(DBD(bot))
