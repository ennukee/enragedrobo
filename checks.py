from discord.ext import commands
import discord.utils
import json
from utils.BotConstants import *

def admins():
	with open('data/admins.json') as f:
		j = json.load(f)
		return [x for x in j if j[x]==1]

# Owner check #
def is_owner_check(message):
    return message.author.id == '126122455248011265'

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


# Admin check (using admins.json) #
def is_admin_check(message):
	return str(message.author.id) in admins()

def is_admin():
	return commands.check(lambda ctx: is_admin_check(ctx.message))


# Not-the-bot check #
def not_bot_check(message):
	return message.author.id != botv.id

def not_bot():
	return commands.check(lambda ctx: not_bot_check(ctx.message))