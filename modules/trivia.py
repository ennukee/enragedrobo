from discord.ext import commands		# Command interface
import discord							# Overall discord library
import datetime, re 					# Datetime and regular expression libraries
import json, asyncio					# json / asyncio libraries
import sys, os 							# Lower-level operations libraries
import requests 						# API queries
import urllib.request 					# Downloading
import random							# Random (RNG)
from time import sleep					# For delays
from collections import defaultdict 
import numpy as np 						# Advanced number/set arithmetic

from utils.Champion import *			# Various champion data related operations
from utils.BotConstants import *
from utils import imageloader 			# Image downloader

class Trivia:
	def __init__(self, bot):
		self.bot = bot
		self.game_types = ['name_to_spell', 'spell_to_name', 'title_to_name', 'name_to_title', 'max_or_min_stat', 'blurb_to_name', 'guess_the_skin']
		self.game_p = [0.16, 0.16, 0.16, 0.16, 0.05, 0.16, 0.15]
		self.wrong_message = "*{}* (guessed {}) is **incorrect**. You have **{}** seconds for anyone else to try again."

	@commands.command(pass_context=True)
	async def trivia(self, ctx, amt : int):
		"""Play some trivia! (use with a number)"""
		if botv.ingame():
			await self.bot.say("Sorry, a game is currently in channel `{}` on **{}** server (by <@{}>)".format(*botv.get_gamedata()))
			return

		winners = defaultdict(int)
		await self.bot.say("**Game: League of Legends trivia!**\n(warning: may occasionally miss an answer, be sure to repeat it if you know it is correct)")
		current_channel = ctx.message.channel.id
		botv.toggle_ingame()
		botv.set_gamedata(ctx.message.channel.name, ctx.message.server.name, ctx.message.author)

		def notother(m):
			m.channel.id == current_channel

		for i in range(0, amt if amt>=1 else 10000):
			await self.bot.say("Question **{}** {}".format(i+1, "of {}".format(amt) if amt>=1 else ""))
			game_type = np.random.choice(self.game_types, p=self.game_p)
			champ_names = [name for name in load_champion_stats()]
			champ_name = random.choice(champ_names)
			data = load_champion_data(champ_name)

			"""For name_to_spell and spell_to_name games"""
			ability_number = random.choice([0,1,2,3,'Passive']) 	# Q, W, E, R, Passive
			ability_name = str(data['spells'][ability_number]['name']) if ability_number != 'Passive' else str(data['passive']['name'])

			"""For name_to_title and title_to_name games"""
			title = data['title']

			print("debug: {}, {} {} {} {}".format(champ_name, title, ability_number, ability_name, [x.strip(' ') for x in re.split(',|/',ability_name.lower())]))
			number_to_letter = {0: 'Q', 1: 'W', 2: 'E', 3: 'R', 'Passive': 'Passive'}
			remaining = 60.0

			if(game_type == 'name_to_spell'):
				possible = [x.strip(' ') for x in re.split(',|/',ability_name.lower())]

				await self.bot.say("What is the name of **{}'s {}**?".format(champ_name, number_to_letter[ability_number]))

				# Standard operations for start of trivia game #
				answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer == None):
					await self.bot.say("Times up, the answer was **{}**!".format(ability_name))
					continue
				while(answer.channel.id != current_channel or answer.author.id == botv.id):
					answer = await self.bot.wait_for_message(timeout=remaining)

				if(answer.content == '!quit'):
					await self.bot.say("Trivia game ended manually by {}".format(ctx.message.author))
					botv.toggle_ingame()
					return
				# End of standard operations for start of trivia game #
				
				while(answer != None and answer.content.lower() not in possible):
					remaining -= 5.0
					hint = "Here's a hint: **{}**".format(ability_name[0:int((60-remaining)/10)])

					if(remaining % 10 == 0):
						await self.bot.say(hint)
					await self.bot.say(self.wrong_message.format(answer.author, answer.content, remaining))
					
					answer = await self.bot.wait_for_message(timeout=remaining)
					while(answer and answer.channel.id != current_channel):
						answer = await self.bot.wait_for_message(timeout=remaining+1)
				if(answer):
					await self.bot.say("**{}** was correct! The answer was **{}**.\n\n".format(answer.author, ability_name))
					winners[answer.author.name]+=1
				else:
					await self.bot.say("Times up, the answer was **{}**!".format(ability_name))

			elif(game_type == 'spell_to_name'):
				await self.bot.say("Whose ability is **{}**? (format example: Annie W)".format(ability_name))
				
				# Standard operations for start of trivia game #
				answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer == None):
					await self.bot.say("Times up, the answer was **{}'s {}**!".format(champ_name, number_to_letter[ability_number]))
					continue
				while(answer.channel.id != current_channel or answer.author.id == botv.id):
					answer = await self.bot.wait_for_message(timeout=remaining)

				if(answer.content == '!quit'):
					await self.bot.say("Trivia game ended manually by {}".format(ctx.message.author))
					botv.toggle_ingame()
					return
				# End of standard operations for start of trivia game #
				
				def is_correct(inp):
					try:
						name = str(re.sub('\'|\s','',''.join(inp.split()[:-1])))
						abil = inp.split()[-1]
						if(name.lower() != champ_name.lower() or abil.lower() != number_to_letter[ability_number].lower()):
							return False
					except Exception as e:
						return False
					return True

				while(answer != None and not is_correct(answer.content)):
					remaining -= 5.0
					hint = "Here's a hint: **{}**".format(champ_name[0:int((60-remaining)/20)])

					if(remaining % 20 == 0):
						await self.bot.say(hint)
					await self.bot.say(self.wrong_message.format(answer.author, answer.content, remaining))
					answer = await self.bot.wait_for_message(timeout=remaining)
					while(answer and answer.channel.id != current_channel):
						answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer):
					await self.bot.say("**{}** was correct! The answer was **{}'s {}**.\n\n".format(answer.author, champ_name, number_to_letter[ability_number]))
					winners[answer.author.name]+=1
				else:
					await self.bot.say("Times up, the answer was **{}'s {}**!".format(champ_name, number_to_letter[ability_number]))

			elif(game_type == 'title_to_name'):
				await self.bot.say("Who is this? {}, {}".format("\_\_\_\_\_\_\_\_", title))
				
				# Standard operations for start of trivia game #
				answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer == None):
					await self.bot.say("Times up, the answer was **{}**!".format(champ_name))
					continue
				while(answer.channel.id != current_channel or answer.author.id == botv.id):
					answer = await self.bot.wait_for_message(timeout=remaining)

				if(answer.content == '!quit'):
					await self.bot.say("Trivia game ended manually by {}".format(ctx.message.author))
					botv.toggle_ingame()
					return
				# End of standard operations for start of trivia game #
				
				def is_correct(inp):
					try:
						name = str(re.sub('\'|\s','',inp)).lower()
						if(name != champ_name.lower()):
							return False
					except Exception as e:
						return False
					return True

				while(answer != None and not is_correct(answer.content)):
					remaining -= 5.0
					hint = "Here's a hint: **{}**".format(champ_name[0:int((60-remaining)/20)])

					if(remaining % 20 == 0):
						await self.bot.say(hint)
					await self.bot.say(self.wrong_message.format(answer.author, answer.content, remaining))
					answer = await self.bot.wait_for_message(timeout=remaining)
					while(answer and (answer.channel.id != current_channel or answer.author.id == botv.id)):
						answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer):
					await self.bot.say("**{}** was correct! The answer was **{}**.\n\n".format(answer.author, champ_name))
					winners[answer.author.name]+=1
				else:
					await self.bot.say("Times up, the answer was **{}**!".format(champ_name))

			elif(game_type == 'name_to_title'):
				await self.bot.say("What is the title for **{}**?".format(champ_name))
				
				# Standard operations for start of trivia game #
				answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer == None):
					await self.bot.say("Times up, the answer was **{}**!".format(title))
					continue
				while(answer.channel.id != current_channel or answer.author.id == botv.id):
					answer = await self.bot.wait_for_message(timeout=remaining)

				if(answer.content == '!quit'):
					await self.bot.say("Trivia game ended manually by {}".format(ctx.message.author))
					botv.toggle_ingame()
					return
				# End of standard operations for start of trivia game #

				while(answer != None and answer.content.lower() != title.lower()):
					remaining -= 5.0
					hint = "Here's a hint: **{}**".format(title[0:int((60-remaining)/10)])

					if(remaining % 10 == 0):
						await self.bot.say(hint)
					await self.bot.say(self.wrong_message.format(answer.author, answer.content, remaining))
					answer = await self.bot.wait_for_message(timeout=remaining)
					while(answer and (answer.channel.id != current_channel or answer.author.id == botv.id)):
						answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer):
					await self.bot.say("**{}** was correct! The answer was **{}**.\n\n".format(answer.author, title))
					winners[answer.author.name]+=1
				else:
					await self.bot.say("Times up, the answer was **{}**!".format(title))

			elif(game_type == 'max_or_min_stat'):
				stat = random.choice(['movespeed','armor','hp','mp','spellblock','attackdamage'])
				readable_stat = {'movespeed': 'movement speed', 'armor': 'armor', 'hp': 'health', 'mp': 'mana', 'spellblock': 'magic resist', 'attackdamage': 'AD'}
				which_one = random.choice(['highest','lowest'])
				data = load_champion_stats()

				if(which_one == 'highest'):
					champ_name = max(data, key = lambda item: int(data[item]['stats'][stat]))
				else:
					champ_name = min(data, key = lambda item: int(data[item]['stats'][stat]))
				value = data[champ_name]['stats'][stat]
				potential_champs = [champ.lower() for champ in data if data[champ]['stats'][stat] == value]

				print("debug 2: {} {} ({}) = {}".format(which_one, readable_stat[stat], stat, champ_name))

				await self.bot.say("Which champion has the **{}** base (level 1) {} in the game?".format(which_one, readable_stat[stat]))

				# Standard operations for start of trivia game #
				answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer == None):
					await self.bot.say("Times up, the answer was **{}** (w/ {} {})!".format(' / '.join(potential_champs), value, readable_stat[stat]))
					continue
				while(answer.channel.id != current_channel or answer.author.id == botv.id):
					answer = await self.bot.wait_for_message(timeout=remaining)

				if(answer.content == '!quit'):
					await self.bot.say("Trivia game ended manually by {}".format(ctx.message.author))
					botv.toggle_ingame()
					return
				# End of standard operations for start of trivia game #

				def is_correct(inp):
					try:
						name = str(re.sub('\'|\s','',inp)).lower()
						if(name not in potential_champs):
							return False
					except Exception as e:
						return False
					return True

				while(answer != None and not is_correct(answer.content)):
					remaining -= 5.0
					hint = "Here's a hint: **{}**".format(champ_name[0:int((60-remaining)/10)])

					if(remaining % 10 == 0):
						await self.bot.say(hint)
					await self.bot.say(self.wrong_message.format(answer.author, answer.content, remaining))
					answer = await self.bot.wait_for_message(timeout=remaining)
					while(answer and (answer.channel.id != current_channel or answer.author.id == botv.id)):
						answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer):
					await self.bot.say("**{}** was correct! The answer was **{}** (w/ {} {}).\n\n".format(answer.author, ' / '.join(potential_champs), value, readable_stat[stat]))
					winners[answer.author.name]+=1
				else:
					await self.bot.say("Times up, the answer was **{}** (w/ {} {})!".format(' / '.join(potential_champs), value, readable_stat[stat]))

			elif(game_type == 'blurb_to_name'):
				reg = re.compile(re.escape(champ_name), re.IGNORECASE)
				blurb = reg.sub('********', data['blurb'].replace('<br>','\n')).replace(data['name'], '*******')
				await self.bot.say("Who does this sound like?\n```\n{}\n```".format(blurb))
				
				# Standard operations for start of trivia game #
				answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer == None):
					await self.bot.say("Times up, the answer was **{}**!".format(champ_name))
					continue
				while(answer.channel.id != current_channel or answer.author.id == botv.id):
					answer = await self.bot.wait_for_message(timeout=remaining)

				if(answer.content == '!quit'):
					await self.bot.say("Trivia game ended manually by {}".format(ctx.message.author))
					botv.toggle_ingame()
					return
				# End of standard operations for start of trivia game #
				
				def is_correct(inp):
					try:
						name = str(re.sub('\'|\s','',inp)).lower()
						if(name != champ_name.lower()):
							return False
					except Exception as e:
						return False
					return True

				while(answer != None and not is_correct(answer.content)):
					remaining -= 5.0
					hint = "Here's a hint: **{}**".format(champ_name[0:int((60-remaining)/20)])

					if(remaining % 20 == 0):
						await self.bot.say(hint)
					await self.bot.say(self.wrong_message.format(answer.author, answer.content, remaining))
					answer = await self.bot.wait_for_message(timeout=remaining)
					while(answer and (answer.channel.id != current_channel or answer.author.id == botv.id)):
						answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer):
					await self.bot.say("**{}** was correct! The answer was **{}**.\n\n".format(answer.author, champ_name))
					winners[answer.author.name]+=1
				else:
					await self.bot.say("Times up, the answer was **{}**!".format(champ_name))

			elif(game_type == 'guess_the_skin'):
				await self.bot.say("What is this skin?")
				skins =  [(ch['name'], ch['num']) for ch in data['skins'] if ch['name'] != 'default']
				skin = random.choice(skins)
				try:
					imageloader.load_splash_art(champ_name, skin[1], champ_names)
				except Exception as e:
					await bot.say('Something went wrong, sorry!')
					continue

				print('debug2: {}'.format(skin))

				await self.bot.send_file(ctx.message.channel, 'data/league/current_splash.jpg')
				
				# Standard operations for start of trivia game #
				answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer == None):
					await self.bot.say("Times up, the answer was **{}**!".format(skin[0]))
					continue
				while(answer.channel.id != current_channel or answer.author.id == botv.id):
					answer = await self.bot.wait_for_message(timeout=remaining)

				if(answer.content == '!quit'):
					await self.bot.say("Trivia game ended manually by {}".format(ctx.message.author))
					botv.toggle_ingame()
					return
				# End of standard operations for start of trivia game #

				while(answer != None and answer.content.lower() != skin[0].lower()):
					remaining -= 5.0
					hint = "Here's a hint: **{}**".format(skin[0][0:int((60-remaining)/10)])

					if(remaining % 10 == 0):
						await self.bot.say(hint)
					await self.bot.say(self.wrong_message.format(answer.author, answer.content, remaining))
					answer = await self.bot.wait_for_message(timeout=remaining)
					while(answer and (answer.channel.id != current_channel or answer.author.id == botv.id)):
						answer = await self.bot.wait_for_message(timeout=remaining)
				if(answer):
					await self.bot.say("**{}** was correct! The answer was **{}**.\n\n".format(answer.author, skin[0]))
					winners[answer.author.name]+=1
				else:
					await self.bot.say("Times up, the answer was **{}**!".format(skin[0]))

			winners_message = "**Current winners:**\n"
			for q in sorted(winners, key=winners.get, reverse=True):
				winners_message += '{}: *{}* correct\n'.format(q, winners[q])
			await self.bot.say(winners_message + '\n')

			delay = 10 if amt >= 1 else 30
			if(i<amt-1 or amt==0):
				await self.bot.say("Next question in {} seconds...".format(delay))
			
			sleep(delay)
		botv.toggle_ingame()

def setup(bot):
	bot.add_cog(Trivia(bot))
