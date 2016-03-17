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

	@commands.command(pass_context=True, hidden=True)
	@checks.is_owner()
	async def evalc(self, ctx, *, code : str):
	    """Evaluates code (via RoboDanny source)"""
	    code = code.strip('` ')
	    python = '```py\n{}\n```'
	    result = None
	    try:
	        result = eval(code)
	    except Exception as e:
	        await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
	        return

	    if asyncio.iscoroutine(result):
	        result = await result
	    await self.bot.say(python.format(result))

def setup(bot):
	bot.add_cog(BotConfig(bot))
