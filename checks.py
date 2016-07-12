from discord.ext import commands
import discord.utils
import json
from utils.BotConstants import *

# Owner check #
def is_owner_check(message):
    return message.author.id == '126122455248011265'

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


# Bot moderator check (using 'Bot Mod' role) #
def is_bot_mod_check(message):
  return 'Bot Mod' in [role.name for role in message.author.roles]

def is_bot_mod():
  return commands.check(lambda ctx: is_bot_mod_check(ctx.message))


# Non-private message check #
def not_private_check(message):
  return not message.channel.is_private

def not_private():
  return commands.check(lambda ctx: not_private_check(ctx.message))


# Not-the-bot check #
def not_bot_check(message):
	return message.author.id != botv.id

def not_bot():
	return commands.check(lambda ctx: not_bot_check(ctx.message))
