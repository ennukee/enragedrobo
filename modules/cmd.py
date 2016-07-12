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


class CommandInterface:
  def __init__(self, bot):
    self.bot = bot

  @commands.command(pass_context=True)
  @checks.not_private()
  async def tag(self, ctx, cmd_name):
    """Used to call commands made by the cmd command"""
    server_id = ctx.message.server.id
    server_cmd_dir = './data/custom_commands/{}'.format(server_id)
    cmd_file = server_cmd_dir + '/{}.json'.format(cmd_name)

    # Check if the server has commands
    if not os.path.isdir(server_cmd_dir) or not os.listdir(server_cmd_dir):
      await self.bot.say('Your server doesn\'t have any commands yet!\n\nUse `help cmd` for more info')

    # Check if specified command exists
    elif not os.path.isfile(cmd_file):
      await self.bot.say('That command does not exist on this server')

    else:
      with open(cmd_file, 'r') as f:
        await self.bot.say(f.read())

  @commands.command(pass_context=True)
  @checks.not_private()
  @checks.is_bot_mod()
  async def cmd(self, ctx, mode, name, *content):
    """Used to create, edit, or remove server-specific custom commands.

    You can use the ADD mode (+ or add) to add a command with <name> and <content>
    You can use the EDIT mode (edit) to edit an existing command
    You can use the REMOVE mode (-, remove or delette) to delete an existing commands

    To use any of the commands made, use the tag command followed by the name of the command you want to use
    """

    add_mode_aliases = ['+','add']
    edit_mode_aliases = ['edit']
    remove_mode_aliases = ['-','remove','delete']

    server_id = ctx.message.server.id
    server_cmd_dir = './data/custom_commands/{}'.format(server_id)
    cmd_file = server_cmd_dir + '/{}.json'.format(name)

    # Checks against edge cases
    if mode in remove_mode_aliases and content:
      await self.bot.say('Do not supply more than the command name when removing a command')
    elif (mode in add_mode_aliases or mode in edit_mode_aliases) and not content:
      await self.bot.say('Please supply content for the command following the command\'s name')
    else:
      # Now onto the logic, but we need to ensure some prereqs

      # Firstly, check if the server's command file exists
      if not os.path.isdir(server_cmd_dir):
        os.mkdir(server_cmd_dir)

      # Add mode
      if mode in add_mode_aliases:
        # We need to check if the command already exists
        if os.path.isfile(cmd_file):
          await self.bot.say('That command already exists on your server. To overwrite an existing command, use **edit** mode')
          return

        # If it doesn't, we shall add it!
        with open(cmd_file, 'w') as f:
          f.write(' '.join(content))
        await self.bot.say('Your command, `{}`, has been added!'.format(name))

      # Edit mode
      if mode in edit_mode_aliases:
        # Check if the command exists in the first place
        if not os.path.isfile(cmd_file):
          await self.bot.say('That command does not exist on your server')
          return

        # If it does, edit it!
        with open(cmd_file, 'w') as f:
          f.write(' '.join(content))
        await self.bot.say('Your command, `{}`, has been changed!'.format(name))

      # Remove move
      if mode in remove_mode_aliases:
        # Check if the command exists in the first place
        if not os.path.isfile(cmd_file):
          await self.bot.say('That command does not exist on your server')
          return

        # If it does, we shall remove it!
        os.remove(cmd_file)
        await self.bot.say('`{}` has been removed!'.format(name))

      
def setup(bot):
  bot.add_cog(CommandInterface(bot))
