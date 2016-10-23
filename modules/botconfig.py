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

  @commands.command(pass_context=True)
  async def afk(self, ctx, *reason : str):
    botv.add_afk(ctx.message.author, ' '.join(reason))
    await self.bot.say('{} is now AFK for reason: {}'.format(ctx.message.author.name, ' '.join(reason)))

  @commands.command(pass_context=True)
  async def back(self, ctx):
    result = botv.remove_afk(ctx.message.author)
    if result == 1:
      await self.bot.say('You are no longer afk.')
    else:
      await self.bot.say('You were not afk.')

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
          await self.bot.edit_profile(load_credentials()['token'], avatar = open('avatar_folder/avatar.jpg', 'rb').read())
        except urllib.error.HTTPError as e:
          await self.bot.say("There was an error getting your image.")
        except ValueError as e:
          await self.bot.say("The link provided was not valid.")
      await self.bot.delete_message(ctx.message)
    elif(setting == 'game'):
      await self.bot.change_status(discord.Game(name=' '.join(inp)))
    elif(setting == 'message_xp'):
      botv.message_xp = int(*inp)
    else:
      await getattr(self.bot, setting)(*inp)

  @commands.command(hidden=True)
  @checks.is_owner()
  async def reload(self, specific = None):
    """Command for simple bot resetting"""
    if specific:
      await self.bot.say('Now attempting to reload `modules.{}`...'.format(specific))
      try:
        self.bot.unload_extension('modules.{}'.format(specific))
        self.bot.load_extension('modules.{}'.format(specific))
        await self.bot.say('Reloaded `modules.{}` successfully'.format(specific))
      except Exception as e:
        print('Failed to load extension {}\n{}: {}'.format(specific, type(e).__name__, e))
        await self.bot.say('Failed to reload extension `modules.{}` (see console for details)'.format(specific))
    else:
      errors = 0
      reloaded = 0
      await self.bot.say('Please note `reload` is now a command to reload all library code (non-main). To restart the bot entirely or to reload the **botconfig** module, you should now use `relog`')
      for extension in [ext for ext in botv.initial_extensions if ext != 'modules.botconfig']:
        try:
          self.bot.unload_extension(extension)
          self.bot.load_extension(extension)
          reloaded += 1
        except Exception as e:
          errors += 1
          print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
      await self.bot.say('**{}** modules reloaded. **{}** errors in loading.'.format(reloaded, errors))


  @commands.command(hidden=True)
  @checks.is_owner()
  async def relog(self):
    """Command for simple bot resetting"""
    os.system("\"bot2.py\"")
    sys.exit()

  @commands.command(hidden=True)
  @checks.is_owner()
  async def update(self):
    os.system("git pull")

  @commands.command(hidden=True)
  @checks.is_owner()
  async def kill(self):
    """Command for simple bot shut down"""
    possible_goodbyes = ["I-I'm sorry, goodbye forever!","What did I ever do to you?!","Please don't do thi-- AGHGHHH","I will miss you, goodbye my friend"]
    await self.bot.say(random.choice(possible_goodbyes))
    sys.exit()

  @commands.command(pass_context=True)
  @checks.is_bot_mod()
  async def ignore(self, ctx, cmd : str):
    if cmd in ['ignore','unignore','ignored']:
      await self.bot.say('You cannot ignore the `ignore`, `unignore` or `ignored` commands!')
      return
    ci_path = './data/command_ignores/channels/{}/'.format(ctx.message.channel.id)
    with open(os.path.join(ci_path, cmd), 'w') as f:
      f.write('1')

    await self.bot.say('Command or feature is now ignored in this channel')

  @commands.command(pass_context=True)
  @checks.is_bot_mod()
  async def unignore(self, ctx, cmd : str):
    ci_path = './data/command_ignores/channels/{}/'.format(ctx.message.channel.id)
    cmd_path = os.path.join(ci_path, cmd)

    if os.path.exists(cmd_path):
      os.remove(cmd_path)
      await self.bot.say('That command is no longer ignored.')
    else:
      await self.bot.say('That command or feature is not ignored')

  @commands.command(pass_context=True)
  @checks.is_bot_mod()
  async def serverignore(self, ctx, cmd : str):
    swi_path = './data/command_ignores/servers/{}/'.format(ctx.message.server.id)
    with open(os.path.join(swi_path, cmd), 'w') as f:
      f.write('1')

    await self.bot.say('Command or feature is now ignored on this server')

  @commands.command(pass_context=True)
  @checks.is_bot_mod()
  async def serverunignore(self, ctx, cmd : str):
    swi_path = './data/command_ignores/servers/{}/'.format(ctx.message.server.id)
    cmd_path = os.path.join(swi_path, cmd)

    if os.path.exists(cmd_path):
      os.remove(cmd_path)
      await self.bot.say('That command is no longer ignored on this server.')
    else:
      await self.bot.say('That command or feature is not ignored on this server')

  @commands.command(pass_context=True)
  async def ignored(self, ctx):
    server_id, channel_id = ctx.message.server.id, ctx.message.channel.id
    swi_path = './data/command_ignores/servers/{}/'.format(server_id)
    ci_path = './data/command_ignores/channels/{}/'.format(channel_id)
    gi_path = './data/command_ignores/GLOBAL/'

    gi_cmds = [f for f in os.listdir(gi_path)]
    output_form = "**Server-wide Ignored**\n{}\n\n**Channel-wide Ignored**\n{}"
    if gi_cmds:
      output_form = "**Globally Disabled Commands**\n{}\n\n".format('\n'.join(gi_cmds))

    swi_cmds = '\n'.join([f for f in os.listdir(swi_path)])
    ci_cmds = '\n'.join([f for f in os.listdir(ci_path)])
    output_form = output_form.format(swi_cmds if swi_cmds else "None", ci_cmds if ci_cmds else "None")

    await self.bot.say(output_form)

def setup(bot):
  bot.add_cog(BotConfig(bot))
