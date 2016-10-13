# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import urllib.request # Downloading
import random # Random (RNG)
import datetime
import time

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

  @commands.command()
  async def choice(self, *choices):
    result = random.choice(choices) if len(choices)>0 else ":upside_down:"
    await self.bot.say('{}'.format(result))

  @commands.command(pass_context=True)
  @checks.is_bot_mod()
  async def massnickname(self, ctx, form):
    server = ctx.message.server

    # In the case of a large 250+ user server...
    if server.large:
      await self.bot.request_offline_members(server)

    users = server.members
    errors = 0
    await self.bot.say('Note: Due to rate limiting, this may take up to {} seconds to complete'.format(len(users) + 2))
    for user in users:
      try:
        await self.bot.change_nickname(user, form.format(user.name) if form != "None" else None)
        time.sleep(1)
      except Exception as e:
        print('[SERVER {}] {}: {}'.format(server.id, type(e).__name__, e))
        errors += 1
        
    await self.bot.say('Done. There was/were **{}** user(s) who were unable to be changed.\n\n*(note: There is almost always 1 person; the server owner. If this is most/all of the server, the bot likely does not have permission to change others\' username)*'.format(errors))
  
  @commands.command()
  async def flip(self, *to_flip : str):
    to_flip = ' '.join(to_flip)
    normal = "abcdefghijklmnopqrstuvwyz"
    flipped = "zʎʍʌnʇsɹbdouɯlʞɾᴉɥƃɟǝpɔqɐ"[::-1]
    flip_emoji = "(╯°□°）╯︵{}"

    result = ""
    botv.set_last_flip(to_flip)
    for c in to_flip:
      try:
        i = normal.index(c)
        result = flipped[i] + result
      except (IndexError,ValueError) as e:
        result = c + result

    await self.bot.say(flip_emoji.format(result))

  @commands.command()
  async def unflip(self):
    unflip_emoji = "{}ノ( ゜-゜ノ)"
    to_say = botv.get_last_flip()
    if to_say:
      await self.bot.say(unflip_emoji.format(to_say))
    else:
      await self.bot.say("NOTHING HAS BEEN FLIPPED!")

def setup(bot):
  bot.add_cog(Misc(bot))
