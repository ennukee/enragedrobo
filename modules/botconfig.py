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


class BotConfig:
  def __init__(self, bot):
    self.bot = bot

  @commands.command(pass_context=True, hidden=True)
  @checks.is_owner()
  async def botconf(self, ctx, setting : str, *inp : str):
    if(setting == 'avatar'):
      i = inp[0]
      if (i[0],i[-1]) != ('`','`'):
        await self.bot.say("Please encase your image in `s please! (top left of most keyboards)")
      else:
        i = i.strip('`')
        try:
          imageloader.load_image(i)
          await self.bot.edit_profile(load_credentials()['password'], avatar = open('avatar_folder/avatar.jpg', 'rb').read())
        except urllib.error.HTTPError as e:
          await self.bot.say("There was an error getting your image.")
        except ValueError as e:
          await self.bot.say("The link provided was not valid.")
      await self.bot.delete_message(ctx.message)
    elif(setting == 'game'):
      await self.bot.change_status(discord.Game(name=' '.join(inp)))

  @commands.command(hidden=True)
  @checks.is_admin()
  async def reload(self):
    """Command for simple bot resetting"""
    os.system("\"bot2.py\"")
    sys.exit()

  @commands.command(hidden=True)
  @checks.is_admin()
  async def kill(self):
    """Command for simple bot shut down"""
    possible_goodbyes = ["I-I'm sorry, goodbye forever!","What did I ever do to you?!","Please don't do thi-- AGHGHHH","I will miss you, goodbye my friend"]
    await self.bot.say(random.choice(possible_goodbyes))
    sys.exit()

  @commands.command(hidden=True, pass_context=True)
  @checks.is_admin()
  async def addcmd(self, ctx, name : str, is_code : bool, output_to_chat : bool, *content : str):
    if(name in custom_command_list()):
      await self.bot.say('There already exists a command with this name!')
      return
    content = (' '.join(content)).strip('`')
    data = {'code': int(is_code), 'output': int(output_to_chat), 'content': content}
    with open('data/custom_commands/{}.json'.format(name), 'w') as f:
      json.dump(data, f)
      await self.bot.say('Successfully added command `{}`'.format(name))

  @commands.command(hidden=True)
  @checks.is_admin()
  async def rmcmd(self, name : str):
    if(name not in custom_command_list()):
      await self.bot.say('That command does not exist!')
    else:
      os.remove('data/custom_commands/{}.json'.format(name))
      await self.bot.say('Command `{}` successfully removed'.format(name))

  @commands.command(pass_context=True)
  async def lock(self, ctx):
    """ Locks a channel and prevents **any** access while it is locked """
    author_channel = ctx.message.author.voice_channel
    if ctx.message.channel.is_private:
      await self.bot.say('This is not available in private messages')
    if author_channel == ctx.message.server.afk_channel:
      await self.bot.say('You cannot lock the AFK channel!')
    elif not ctx.message.author.permissions_in(ctx.message.channel).move_members:
      await self.bot.say('You do not have sufficient permissions to lock this channel')
    elif not ctx.message.server.afk_channel:
      await self.bot.say('You cannot lock a channel on a server without an AFK channel')
    elif botv.private_channel is not None:
      await self.bot.say('There is already a locked channel, sorry')
    else:
      
      if author_channel: 
        if ctx.message.server.me.permissions_in(author_channel).move_members:
          botv.set_private_channel((ctx.message.author, author_channel))
          await self.bot.say('Channel **{}** has been locked by {}'.format(author_channel.name, ctx.message.author.name))
        else:
          await self.bot.say('I cannot lock a channel if I do not have permissions to move players')

  @commands.command(pass_context=True)
  async def unlock(self, ctx):
    """ Unlock the locked channel (if there is one)"""
    if botv.private_channel is None:
      await self.bot.say('There is no locked channel')
    elif not ctx.message.author.permissions_in(ctx.message.channel).move_members:
      await self.bot.say('You do not have sufficient permissions to unlock this channel')
    else:
      await self.bot.say('Channel **{0.name}** unlocked by **{1.name}** (originally locked by **{2.name}**)'.format(botv.private_channel[1], ctx.message.author, botv.private_channel[0]))
      botv.set_private_channel(None)

  @commands.command(pass_context=True)
  @checks.is_admin()
  async def channelkick(self, ctx):
    """ Removes all users from the channel the typer is in """
    if not ctx.message.author.voice_channel:
      await self.bot.say('You are not in a voice channel')
    elif not ctx.message.server.afk_channel:
      await self.bot.say('Server must have an AFK channel to use this command')
    else:
      for person in ctx.message.author.voice_channel.voice_members:
        await self.bot.move_member(person, ctx.message.server.afk_channel)

def setup(bot):
  bot.add_cog(BotConfig(bot))
