# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import urllib.request # Downloading
import urllib
import requests
import random # Random (RNG)
import datetime
import numpy as np

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sqlite3
import io

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils.BasicUtility import *
from utils.BotConstants import *
from utils import imageloader # Image downloader
from utils.Level import *

class LevelUp:
  """Holds all the logic for the bot's leveling system"""
  def __init__(self, bot):
    self.bot = bot
    self.last_trained = {}
    self.last_saved = {}
    self.gamble_lock = {}
    self.lock_timers = {'save': 7200, 'gamble': 120, 'pot': 20, 'train': 3600}
    self.pot_active_channels = {}
    self.raid = {
      'boss': 
        {
          'name': '', 
          'health': 0, 
          'maxhealth': 0,
          'kill_order': ""
        }, 
      'cooldown': {}, 
      'contribution': {},
      'respawn_timer': 14400,
      'attack_cooldown': 360,
      'died_at': 0,
      'boss_names': ['Chromus', 'Al\'sharah', 'Venomancer', 'Tishlaveer', 'Autrobeen'],
      'five_percent_bonus': 5000,
      'twenty_percent_bonus': 7500,
      'attack_length': 10
    }

  @commands.command()
  async def levelhelp(self):
    """A helper function for all the stuff in the levelup game / module"""
    events = []
    events.append('Welcome to enragedrobo\'s **LevelUP** game!\n')
    events.append('`summary` - Display a summary of all vital cooldowns')
    events.append('`level` - Display a card containing your LevelUP information!')
    events.append('`train` - Unlocks at level **5**. Gives a boost in XP, can be very high if you are lucky. 1 hour cooldown.')
    events.append('`gamble <amount>` - Gamble a certain amount of XP for a chance at glorious prizes!')
    events.append('`pot <amount>` - Open a pot for an amount of XP. The lowest roll pays the highest!')
    events.append('`grace` - Shows the remaining time on the Grace of Light!')
    events.append('`color <mode> <r> <g> <b>` - Set the color for your `xp` or `text`')
    events.append('`lookup <player>` - Use this command with an @ mention to see that person\'s LevelUP data!')
    events.append('`boss <attack>` - Fight a powerful foe with friends!')

    await self.bot.say('\n'.join(events))

  @commands.command(pass_context = True)
  async def summary(self, ctx):
    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute('SELECT * FROM Users WHERE id = {}'.format(author_id)).fetchone()

    exp = user[2]
    level = int(user[3])
    s_score = user[1]

    gamble_remaining, train_remaining, grace_remaining, boss_remaining = 0, 0, 0, 0

    cur_time = datetime.datetime.now()
    # Gamble timer
    last = self.gamble_lock.get(author_id, None)
    if last:
      since_last = (cur_time - last).total_seconds()
      if since_last < self.lock_timers['gamble']:
        gamble_remaining = int(self.lock_timers['gamble'] - since_last)
    last, since_last = 0, 0

    # Train timer
    last = self.last_trained.get(author_id, None)
    if last:
      since_last = (cur_time - last).total_seconds()
      if since_last < self.lock_timers['train']:
        train_remaining = int((self.lock_timers['train'] - since_last)/60)
    last, since_last = 0, 0

    # Grace timer
    last = self.last_saved.get(author_id, None)
    if last:
      since_last = (cur_time - last).total_seconds()
      if since_last < self.lock_timers['save']:
        grace_remaining = int((self.lock_timers['save'] - since_last)/60)
    last, since_last = 0, 0

    # Boss timer
    last = self.raid['cooldown'].get(author_id, None)
    if last:
      since_last = (cur_time - last).total_seconds()
      if since_last < self.raid['attack_cooldown']:
        boss_remaining = int(self.raid['attack_cooldown'] - since_last)
    last, since_last = 0, 0

    def format_time_remaining(i, label):
      if i == 0:
        return "**Up!**"
      else:
        return "**{}** {}".format(i, label)

    events = []
    events.append('<@{}>\n'.format(author_id))
    events.append('**Level {}** ({} EXP)'.format(level, exp))
    events.append('Gamble: {}'.format(format_time_remaining(gamble_remaining, 'seconds')))
    events.append('Boss: {}'.format(format_time_remaining(boss_remaining, 'seconds')))
    events.append('Train: {}'.format(format_time_remaining(train_remaining, 'minutes')))
    events.append('Grace: {}'.format(format_time_remaining(grace_remaining, 'minutes')))

    print(events)

    await self.bot.say('\n'.join(events))


  @commands.command(pass_context=True)
  async def boss(self, ctx, attacks : str):
    def proper_form(s):
      return len(s) == self.raid['attack_length'] and all(x in "ADSBEF" for x in s)
    if not proper_form(attacks):
      await self.bot.say('Attacks must be a ten-character string consisting of A, D, S, B, E, and F (attack, defend, savage, block, execute, flee)')
      return

    if self.raid['died_at'] != None:
      # Boss generation
      if self.raid['died_at'] != 0:
        death_time = self.raid.get('died_at', None)
        time_since_death = (datetime.datetime.now() - death_time).total_seconds() if death_time else 100000
      else:
        time_since_death = 100000

      if time_since_death > self.raid['respawn_timer']:
        # Let's make a new boss
        await self.bot.say('***A powerful new strength appears...***')
        new_name = random.choice(self.raid['boss_names'])
        health = random.randint(50000, 75000)

        self.raid['boss']['name'] = new_name
        self.raid['boss']['health'] = health
        self.raid['boss']['maxhealth'] = health
        self.raid['cooldown'] = {}
        self.raid['contribution'] = {}
        self.raid['died_at'] = None
        self.raid['boss']['kill_order'] = [random.choice("ADSBEF") for x in "1" * self.raid['attack_length']]
      else:
        mins_left = int((self.raid['respawn_timer'] - time_since_death) / 60)
        await self.bot.say('The corpse of {} still lies, rotting away...\n(Respawn in {} minutes)'.format(self.raid['boss']['name'], mins_left))
        return

    # Boss time!
    events = []
    events.append('A **{}** stands before you...'.format(self.raid['boss']['name']))

    perc_health = int(self.raid['boss']['health'] / self.raid['boss']['maxhealth'] * 1000) / 10
    events.append('Health: {}% ({} / {})\n'.format(perc_health, self.raid['boss']['health'], self.raid['boss']['maxhealth']))

    # Player info
    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute('SELECT * FROM Users WHERE id = {}'.format(author_id)).fetchone()

    exp = user[2]
    level = int(user[3])
    s_score = user[1]
    prestige = user[4]

    attack_cd = self.raid['cooldown'].get(author_id, None)
    time_since_attack = (datetime.datetime.now() - attack_cd).total_seconds() if attack_cd else 100000
    if time_since_attack < self.raid['attack_cooldown']:
      mins_left = int((self.raid['attack_cooldown'] - time_since_attack) / 60)
      t = "minutes"
      if mins_left == 0:
        mins_left = int(self.raid['attack_cooldown'] - time_since_attack)
        t = "seconds"
      await self.bot.say('You are too tired to attack yet, try again in {} {}.'.format(mins_left, t))
      return

    correct_order = self.raid['boss']['kill_order']
    num_correct = sum([attacks[i] == correct_order[i] for i in range(0, self.raid['attack_length'])])
    output_form = [":white_check_mark:" if attacks[i] == correct_order[i] else ":x:" for i in range(0, self.raid['attack_length'])]
    damage_dealt = int((num_correct / 7) * random.randint(int(25 * level * (1 + 0.1 * prestige)), int(45 * level * (1 + 0.1 * prestige))))
    
    if num_correct >= 7:
      self.raid['boss']['kill_order'][random.randint(0, self.raid['attack_length'])] = random.choice('ADSBEF')

    if num_correct == 8:
      events.append('You exposed most of the boss\' weak points, 5x damage!')
      damage_dealt *= 5
    elif num_correct == 9:
      events.append('You exposed almost all of the boss\' weak points, **10x** damage!')
      damage_dealt *= 10
    elif num_correct == 10:
      events.append('You exposed ALL of the boss\' weak points, ***25x*** damage!')
      damage_dealt *= 25

    events.append('Your moves were... {}\nYou deal **{}** damage to the boss!'.format(' '.join(output_form), damage_dealt))

    self.raid['boss']['health'] -= damage_dealt
    contribution = self.raid['contribution'].get(author_id, 0)
    self.raid['contribution'][author_id] = contribution + damage_dealt
    self.raid['cooldown'][author_id] = datetime.datetime.now()

    # Check if boss is now dead
    if self.raid['boss']['health'] < 0:
      self.raid['died_at'] = datetime.datetime.now()
      events.append('\n**{} has fallen!**\n'.format(self.raid['boss']['name']))
      events.append('**Contribution**')
      h_user, h_contr = '', 0
      for k, v in self.raid['contribution'].items():
        if v > h_contr:
          h_user = k
          h_contr = v
        perc_contr = int(v / self.raid['boss']['maxhealth'] * 10000) / 100
        events.append('**<@{}> did {} damage** ({}%)'.format(k, v, perc_contr))

      events.append('For doing the most damage, <@{}> gets a `?train` and `?grace` reset.\n'.format(h_user))
      self.last_trained[h_user] = None
      self.last_saved[h_user] = None
      events.append('Everyone who did at least five percent of the damage gains **5000** EXP.')
      events.append('Anyone who did at least twenty percent gains an additional **7500** EXP.')
      events.append('**NOTE**: Prestige has reduced bonuses from raids.')

      for k, v in self.raid['contribution'].items():
        how_much = None
        if v > self.raid['boss']['maxhealth'] / 20:
          user = c.execute('SELECT * FROM Users WHERE id = {}'.format(k)).fetchone()
          exp = user[2]
          s_score = user[1]
          prestige = user[4]

          how_much = 5

          exp_gain = self.raid['five_percent_bonus'] * (1 + prestige * 0.1)
          if v > self.raid['boss']['maxhealth'] / 5:
            how_much = 20
            exp_gain += self.raid['twenty_percent_bonus'] * (1 + prestige * 0.1)

          c.execute('UPDATE Users SET exp = {}, score = {} WHERE ID = {}'.format(exp + exp_gain, s_score + exp_gain, k))
          conn.commit()

        if how_much:
          u_data = read_user_json(k)
          if u_data.get('valid', False):
            if how_much >= 5:
              u_data['five_percent_medal'] = True
            if how_much >= 20:
              u_data['twenty_percent_medal'] = True

          write_user_json(k, u_data)


    await self.bot.say('\n'.join(events))


  @commands.command(pass_context=True)
  async def prestige(self, ctx):
    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute('SELECT * FROM Users WHERE id = {}'.format(author_id)).fetchone()

    exp = user[2]
    level = int(user[3])
    s_score = user[1]
    prestige = user[4]

    u_data = read_user_json(author_id)
    required_level = (1 + prestige // 5) * 25
    exp_consumed = sum([calculate_xp_for_lvl(i) for i in range(1, required_level)])

    if level < required_level:
      await self.bot.say('The **Grace of Light** speaks to you...\n"You are not yet ready, come back when you reach level **{}**"'.format(required_level))
      return

    # Check for medals
    if prestige >= 10:
      required_medal = u_data.get('twenty_percent_medal', None)
      if not required_medal:
        await self.bot.say('"Your power is massive, but lack the accolades to show for it..."\n*(Required: Contribute twenty percent damage to a boss kill)*')
        return
    elif prestige >= 5:
      required_medal = u_data.get('five_percent_medal', None)
      if not required_medal:
        await self.bot.say('"You hold a great power, but you must use it well to move onward."\n*(Required: Contribute five percent damage to a boss kill)*')
        return

    events = []
    events.append('The **Grace of Light** speaks to you...\n')
    events.append('You are worthy of raising your **prestige**.')
    events.append('If you do so, you will lose all the XP needed to go from 1 to {} ({})'.format(required_level, exp_consumed))
    events.append('Your overall ranking will also be dropped in this process.')
    events.append('However, you will permanently earn 100 percent extra experience and both `?grace` and `?train` will be reset.\n')
    events.append('You will keep the ability to do `?setbg`, but will have to re-level for anything else.\n')
    events.append('**Are you sure you want to prestige?** (y/n)')

    await self.bot.say('\n'.join(events))

    def check(msg):
      return msg.content.lower() in ['y','n'] and msg.channel.id == ctx.message.channel.id
    
    msg = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, check=check)
    if msg is None:
      await self.bot.say('Come again another time, then. (Time ran out!)')
    else:
      if msg.content.lower() == 'y':
        c.execute('UPDATE Users SET exp = {}, score = {}, level = 1, prestige = {} WHERE id = {}'.format(s_score - exp_consumed, s_score - exp_consumed, prestige + 1, author_id))
        conn.commit()

        self.gamble_lock[author_id] = None
        self.last_saved[author_id] = None
        self.last_trained[author_id] = None
        await self.bot.say('Very well, you are now **Prestige {}**'.format(prestige + 1))
        if required_level == 50:
          u_data['five_percent_medal'] = None
          write_user_json(author_id, u_data)
        elif required_level >= 75:
          u_data['twenty_percent_medal'] = None
          write_user_json(author_id, u_data)

        if prestige + 1 == 1:
          await self.bot.say('**Prestige 1** Perks\nYou can now do `?color background` to set the background color of `?level`')
      else:
        await self.bot.say('Come again when you are prepared.')


  @commands.command(pass_context=True, hidden=True)
  @checks.is_owner()
  async def override(self, ctx, u_id : int, amt : int):
    if u_id == 0:
      self.raid['boss']['health'] = amt
    else:
      conn = sqlite3.connect('users.db')
      c = conn.cursor()
      user = c.execute('UPDATE Users SET exp = {}, score = {}, level = 1 WHERE ID = {}'.format(amt, amt, u_id))
      conn.commit()

  @commands.command(pass_context=True)
  async def color(self, ctx, mode : str, r : int, g : int, b : int):
    if mode not in ['xp', 'text', 'background']:
      await self.bot.say('Supported modes: `xp`, `background` and `text`')
      return

    old_values = {'xp': (190, 190, 170), 'text': (60, 60, 70)}
    u_data = read_user_json(ctx.message.author.id)
    if any(x < 0 for x in [r,g,b]):
      u_data[mode] = old_values[mode]
    else:
      u_data[mode] = (r, g, b)
      if mode == 'background':
        await self.bot.say('**NOTE**: `background` color changes will not appear until Prestige 1')
    write_user_json(ctx.message.author.id, u_data)

  @commands.command(pass_context=True)
  async def lookup(self, ctx):
    ments = ctx.message.mentions
    if len(ments) >= 1:
        u_id = ments[0].id

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        user = c.execute('SELECT * FROM Users WHERE id = {}'.format(u_id)).fetchone()

        if user:
            exp = user[2]
            level = int(user[3])
            s_score = user[1]
            prestige = user[4]
            max_exp = calculate_xp_for_lvl(level)
            await self.bot.say('<@{}>\nLevel **{}** (Prestige {})\nEXP: {}\{}\nScore: {}'.format(u_id, level, prestige, exp, max_exp, s_score))



  @commands.command(pass_context=True)
  async def pot(self, ctx, cap : int):
    if self.pot_active_channels.get(ctx.message.channel.id, None):
        await self.bot.say('A pot is already active in this channel!')
        return
    elif cap < 1:
        await self.bot.say('A pot must be at least 1 EXP! (sorry reverse potters)')
        return
    players = []

    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    await self.bot.say('**{}** has opened a pot of **{}**\nType \'in\' to join! You have 20 seconds to join.'.format(ctx.message.author.name, cap))
    self.pot_active_channels[ctx.message.channel.id] = '1'

    def check(msg):
        return msg.content.lower() == 'in' and msg.channel.id == ctx.message.channel.id

    start_time = datetime.datetime.now()
    cur_time = datetime.datetime.now()
    while (cur_time - start_time).total_seconds() < self.lock_timers['pot']:
        msg = await self.bot.wait_for_message(timeout=5, check=check)
        if msg is not None:
            a_id = msg.author.id
            user = c.execute('SELECT * FROM Users WHERE id = {}'.format(a_id)).fetchone()
            exp = user[2]
            if exp < cap:
                await self.bot.say('You don\'t have enough exp to enter this pot (required: **{}**)'.format(cap))
            elif a_id not in players:
                await self.bot.say('Player <@{}> registered'.format(a_id))
                players.append(a_id)
        cur_time = datetime.datetime.now()

    if len(players) < 2:
        await self.bot.say('Sorry, pots require at least 2 players.')
        self.pot_active_channels[ctx.message.channel.id] = None
        return

    events = []
    events.append('**Beginning the pot...**\nReward: **{}** XP\n'.format(cap))

    first_roll = random.randint(0,10000)
    rolls = [first_roll]
    events.append('<@{}> has rolled **{}**'.format(players[0], first_roll))
    lowest = 0
    highest = 0
    for i in range(1, len(players)):
        a = random.randint(0,10000)
        while a in rolls:
            a = random.randint(0,10000)
        if a > max(rolls):
            highest = i
        if a < min(rolls):
            lowest = i
        rolls.append(a)
        events.append('<@{}> has rolled **{}**'.format(players[i], a))

    events.append('\nWinner: <@{}>\nLoser: <@{}>'.format(players[highest], players[lowest]))

    await self.bot.say('\n'.join(events))

    highest_user = c.execute('SELECT * FROM Users WHERE id = {}'.format(players[highest])).fetchone()
    lowest_user = c.execute('SELECT * FROM Users WHERE id = {}'.format(players[lowest])).fetchone()
    h_exp, h_score = highest_user[2], highest_user[1]
    l_exp, l_score = lowest_user[2], lowest_user[1]

    c.execute('UPDATE Users SET exp = {}, score = {} WHERE id = {}'.format(h_exp + cap, h_score + cap, players[highest]))
    c.execute('UPDATE Users SET exp = {}, score = {} WHERE id = {}'.format(l_exp - cap, l_score - cap, players[lowest]))
    conn.commit()

    self.pot_active_channels[ctx.message.channel.id] = None


  @commands.command(pass_context=True)
  async def grace(self, ctx):
    author_id = ctx.message.author.id

    recently_saved = self.last_saved.get(author_id, None)
    time_since_last = (datetime.datetime.now() - recently_saved).total_seconds() if recently_saved else 100000

    if time_since_last > self.lock_timers['save']:
        await self.bot.say('The **Grace of Light** is at your side')
    else:
        mins_left = int((self.lock_timers['save'] - time_since_last)/60)
        await self.bot.say('The **Grace of Light** can save you again in {} minutes.'.format(mins_left))

  @commands.command(pass_context=True)
  async def gamble(self, ctx, offer : int):
    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute('SELECT * FROM Users WHERE id = {}'.format(author_id)).fetchone()

    offer = int(offer)

    exp = user[2]
    level = int(user[3])
    s_score = user[1]
    max_exp = calculate_xp_for_lvl(level)
    prestige = user[4]

    new_exp = exp
    new_score = s_score

    gamble_lock = self.gamble_lock.get(author_id, None)
    since_gamble_lock = (datetime.datetime.now() - gamble_lock).total_seconds() if gamble_lock else 100000

    if level < 5:
        await self.bot.say("You need to be **level 5** to use this!")
        return
    elif since_gamble_lock < self.lock_timers['gamble']:
        mins_left = int((self.lock_timers['gamble'] - since_gamble_lock)/60)
        await self.bot.say('You are too afraid to attempt to gamble yet. Try again in {} minutes.'.format(mins_left))
        return
    elif exp < offer:
        await self.bot.say('You do not have that much XP to offer')
        return
    elif offer < max_exp / 8:
        await self.bot.say('You need to offer at least one eighth of your level ({})'.format(max_exp / 8))
        return

    self.gamble_lock[author_id] = None

    # Chances
    # 40.0% -> Lose XP
    # 30.0% -> Locked
    # 7.5-% -> Double XP
    # 10.0% -> Instant level
    # 10.0% -> Reset training
    # 2.50% -> Boss fight

    options = ['lose', 'lock', 'double', 'level', 'reset_training', 'boss'] 
    result = np.random.choice(options, p = [0.40, 0.325, 0.075, 0.1, 0.1, 0])

    if result == 'lose':
        recently_saved = self.last_saved.get(author_id, None)
        time_since_last = (datetime.datetime.now() - recently_saved).total_seconds() if recently_saved else 100000

        if time_since_last > self.lock_timers['save']:
            self.last_saved[author_id] = datetime.datetime.now()
            await self.bot.say('You would have lost offering, but the Grace of Light has saved it. You cannot be saved for another two hours.')
        else:
            await self.bot.say('Unfortunately, the black magic steals away part of you. You lose the offering.')
            new_exp -= offer
            new_score -= offer
    elif result == 'lock':
        await self.bot.say('You feel the dark magic choke you. You do not dare try again for **2 minutes**')
        self.gamble_lock[author_id] = datetime.datetime.now()
    elif result == 'double':
        new_exp += offer * (1 + prestige)
        new_score += offer * (1 + prestige)
        await self.bot.say('You feel the black magic grace you with a gift. You gain back your offering and more.')
    elif result == 'level':
        gain = int((max_exp - exp) * random.random()) * (1 + prestige)
        await self.bot.say('The black magic courses through you. You gain a portion of your remaining level.')
        new_exp += gain 
        new_score += gain 
    elif result == 'reset_training':
        if offer < max_exp / 4:
            await self.bot.say('You feel slightly refreshed, but the offering was not enough to fully refresh you.\n(Sacrifice at least a fourth of a level to unlock this result)')
        else:
            await self.bot.say('The black magic refreshes you. You can use ?train again.')
            self.last_trained[author_id] = None
    elif result == 'boss':
        await self.bot.say('You feel the presence of a very dangerous being. Do you continue? (Y/N)')

        def valid(msg):
            return msg.content.lower() in ['y','n']
        msg = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, check=valid)

        if msg and msg.content.lower() == 'y':
            bosses = ['Chromus', 'Al\'sharah', 'Venomancer', 'Tishlaveer', 'Autrobeen']
            boss_descriptions = {
                'Chromus': 'A being of massive arcane power. His defensive power is overwhelming but has very long wind-up time for his attacks.',
                'Al\'sharah': 'A vicious jungle-dweller. His attacks are ruthless and is an extremely impatient being.',
                'Venomancer': 'Large, crystalline scorpion. Deals damage constantly to anyone nearby. Weak shell.',
                'Tishlaveer': 'A mana-starved being. Will resort to anything to draw mana from his foes. Will wither and die if left alone.',
                'Autrobeen': 'The brother of Chromus. An imperial soldier from the celestial realm. Extremely by-the-books fighter.'
            }

            # Don't care to hide it, tbh
            valid_moves = {
                'Chromus': ['S', 'S', 'S', 'B', 'S', 'S', 'S'],
                'Al\'sharah': ['F', 'B', 'B', 'F', 'C', 'B', 'C'],
                'Venomancer': ['F', 'F', 'F', 'F', 'S', 'S', 'S'],
                'Tishlaveer': ['F', 'G', 'D', 'F', 'G', 'D', 'S'],
                'Autrobeen': ['S', 'F', 'D', 'A', 'D', 'A', 'A']
            }
            chosen_boss = random.choice(bosses)
            b_level = random.randint(level * 4, level * 5)

            events = []
            events.append(':exclamation: **You find a Level {} {}** :exclamation:'.format(b_level, chosen_boss))
            events.append(boss_descriptions[chosen_boss])
            events.append('\nChoose a sequence of seven actions and put them in one message. You have **60 seconds**. The choices are:')
            events.append('**A** - Attack the enemy')
            events.append('**D** - Raise a defense')
            events.append('**S** - Savagely attack the opponent, focusing solely on damage')
            events.append('**B** - Bolster a monstrous defense, focusing only on defending the incoming attack')
            events.append('**F** - Flee from the enemy, backing away a large distance')
            events.append('**G** - Dodge an incoming attack')
            events.append('**C** - Attempt to counter an incoming attack')
            events.append('There is only **one** successful combination of moves.')

            await self.bot.say('\n'.join(events))
            events = ['**Result of the battle...**\n']

            def move_check(msg):
                return all(x in 'ADSBFDC' for x in msg.content) and len(msg.content) == 7
            msg = await self.bot.wait_for_message(timeout=60, author=ctx.message.author, check=move_check)
            if msg is None:
                await self.bot.say('The being escapes your potential attack. (Time up!)')
                return

            moveset = valid_moves[chosen_boss]
            correct_moves = 0

            def move(m, msg, moveset, correct_moves, c_msg, sc, sc_msg, wrong):
                if msg.content[m] == moveset[m]:
                    events.append(":white_check_mark: | " + c_msg)
                    return correct_moves + 1
                elif msg.content[m] == sc:
                    events.append(":ok: | " + sc_msg)
                else:
                    events.append(":x: | " + wrong)
                return correct_moves

            m = 0
            if chosen_boss == 'Chromus':
                # MOVE 1
                correct_moves = move(m, msg, moveset, correct_moves,
                    'You savagely strike at the arcane being. He is too busy charging to defend.', 
                    'A', 
                    'A basic attack doesn\'t seem to affect him much...', 
                    'The being simply charges his power...')
                m += 1

                # MOVE 2
                correct_moves = move(m, msg, moveset, correct_moves,
                    'You savagely strike at the arcane being. He is too busy charging to defend.', 
                    'A', 
                    'A basic attack doesn\'t seem to affect him much...', 
                    'The being simply charges his power...')
                m += 1

                # MOVE 3
                correct_moves = move(m, msg, moveset, correct_moves,
                    'You savagely strike at the arcane being. He looks like he is about to strike.', 
                    'A', 
                    'A basic attack doesn\'t seem to affect him much, but you can tell he is about to strike next', 
                    'The being simply charges his power. He is about to release his power.')
                m += 1

                # MOVE 4
                correct_moves = move(m, msg, moveset, correct_moves,
                    'You bolster the strongest defense you can and take the brunt of his massive attack successfully',
                    'D', 
                    'The attack overwhelms your defenses and inflicts severe mana burns',
                    'The being releases an overwhelmingly powerful attack that strikes everywhere in the area. You sustain severe mana burns.')
                m += 1

                # MOVE 5
                correct_moves = move(m, msg, moveset, correct_moves,
                    'You savagely strike at the arcane being. He is too busy charging to defend.', 
                    'A', 
                    'A basic attack doesn\'t seem to affect him much...', 
                    'The being simply charges his power...')
                m += 1

                # MOVE 6
                correct_moves = move(m, msg, moveset, correct_moves,
                    'You savagely strike at the arcane being. He is too busy charging to defend.', 
                    'A', 
                    'A basic attack doesn\'t seem to affect him much... He looks to be trying to retreat', 
                    'The being simply charges his power... but he looks scared now')
                m += 1

                # MOVE 7
                correct_moves = move(m, msg, moveset, correct_moves,
                    'You savagely strike at the arcane being. He falls to the ground, defeated', 
                    'A', 
                    'A basic attack doesn\'t seem to affect him much. He is able to channel enough energy to teleport away', 
                    'The being teleports away')
                m += 1

            elif chosen_boss == 'Al\'sharah':
                print('PH')
            elif chosen_boss == 'Venomancer':
                print('PH')
            elif chosen_boss == 'Tishlaveer':
                print('PH')
            elif chosen_boss == 'Autrobeen':
                print('PH')

            events.append('\n**Correct Moves:** {}'.format(correct_moves))
            events.append('**EXP Gained**: {}'.format(level * 10 * correct_moves * (1 + prestige)))
            new_exp += level * 10 * correct_moves
            new_score += level * 10 * correct_moves
            await self.bot.say('\n'.join(events))

        else:  
            await self.bot.say('Probably a wise choice...')

    c.execute('UPDATE Users SET exp = {}, score = {} WHERE id = {}'.format(new_exp, new_score, author_id))
    conn.commit()


  @commands.command(pass_context=True)
  async def train(self, ctx):
    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute('SELECT * FROM Users WHERE id = {}'.format(author_id)).fetchone()

    exp = user[2]
    level = int(user[3])
    s_score = user[1]
    prestige = user[4]

    if level < 5:
        await self.bot.say("You need to be **level 5** to use this!")
        return

    last_session = self.last_trained.get(author_id, None)
    time_since_last = (datetime.datetime.now() - last_session).total_seconds() if last_session else 100000

    WAIT_TIME = 3600

    if not last_session or time_since_last > WAIT_TIME:
        self.last_trained[author_id] = datetime.datetime.now()

        events = ['You begin training...\n']

        exp_gain = level * 12 * (1 + prestige)
        global_multiplier = 1 
        chance_of_occurring = 1.0
        i = 2 if time_since_last > WAIT_TIME*2 else 3
        r = random.randint(1,i)
        while r == 1:
            event_poss = ['You feel great improvement', 'You recognize a new way to maximize your training', 'Your blade feels swifter than before', 'You dodge a quick foe']
            event_chosen = random.choice(event_poss)

            local_multiplier = random.randint(15,25) / 10
            exp_gain *= local_multiplier
            global_multiplier *= local_multiplier

            chance_of_occurring /= float(i)
            event_chosen += ' (Chance: **{}**%)'.format(round(chance_of_occurring*100, 3))
            events.append(event_chosen)
            i += 1
            r = random.randint(1,i)
        if chance_of_occurring == 1.0:
            events.append('You didn\'t benefit much from basic training...')

        events.append('\nYou begin fighting some monsters in the forest...')
        num_encounters = random.randint(1, int(level / 3))
        while num_encounters > 0:
            m_level = random.randint(int(level / 2), level * 3)
            monster_types = ['Peon', 'Soldier', 'Captain', 'General', 'King', 'God']
            monster_mults = {
                             'Peon': 0.25, 
                             'Soldier': 1, 
                             'Captain': 1.25, 
                             'General': 2.0,
                             'King': 20.0,
                             'God': 100.0
                            }
            m_type = np.random.choice(monster_types, p=[0.15, 0.4, 0.25, 0.15, 0.04, 0.01])
            m_mult = monster_mults[m_type]

            player_stronger = level > m_level
            level_diff = abs(level - m_level)
            win_chance = 0.5
            if player_stronger:
                win_chance = 0.5 + (1/2) * pow(1 / (level / 2), 2) * pow(level_diff, 2)
            elif level_diff == 0:
                win_chance = 0.5
            else:
                win_chance = 0.5 + (-1/2) * pow(1 / (level * 2), 2) * pow(level_diff, 2)

            win_chance /= m_mult
            exp_for_winning = 0
            win_perc = round(win_chance * 100, 3) if win_chance < 1 else 100
            if random.random() < win_chance:
                exp_for_winning = m_level * m_mult * global_multiplier * (1 + prestige)
                exp_gain += exp_for_winning
                events.append('You *beat* a Lv. **{}** **{}** (EXP: +**{}**) (Chance: **{}%**)'.format(m_level, m_type, exp_for_winning, win_perc))
            else:
                events.append('You *lost* to a Lv. **{}** **{}** (Chance: **{}%**)'.format(m_level, m_type, win_perc))
            num_encounters -= 1
        
        exp_gain = int(exp_gain)

        events.append('\nYou gained **{}** XP!'.format(exp_gain))

        await self.bot.say('\n'.join(events))

        new_exp = exp + exp_gain
        new_score = s_score + exp_gain
        c.execute('UPDATE Users SET exp = {}, score = {} WHERE id = {}'.format(new_exp, new_score, author_id))
        conn.commit()

    else:
        minutes_left = int((WAIT_TIME - time_since_last)/60)
        await self.bot.say('You are still too tired to train again, try again in {} minutes.'.format(minutes_left))

  @commands.command(pass_context=True)
  async def setbg(self, ctx, img):
    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute('SELECT * FROM Users WHERE id = {}'.format(author_id)).fetchone()

    if int(user[3]) < 25 and int(user[4]) == 0:
        await self.bot.say('You must be level **25** or prestige **1** to set custom backgrounds!')
        return

    custom_img = './data/levelup/users/levelup_bg_{}.jpg'.format(author_id)
    if img in [None, "None"]:
        if os.path.isfile(custom_img):
            os.remove(custom_img)
            return
        else:
            await self.bot.say('You do not have a custom background')
            return

    try:
        imageloader.load_background(img, author_id)
    except ValueError as e:
        await self.bot.say('The image link was invalid')
    except urllib.error.HTTPError as e:
        await self.bot.say('The requested image denied me :frowning:. Consider reuploading it to a source like imgur.')
    except Exception as e:
        await self.bot.say('Something went wrong during processing.\n{}: {}'.format(type(e).__name__, e))

    img = Image.open(custom_img)
    th_size = 300, 100
    draw = ImageDraw.Draw(img, 'RGBA')

    w, h = img.size

    new_dim = 320, int(h / (w / 300))
    img_resize = img.resize(new_dim, Image.ANTIALIAS)
    img_cropped = img_resize.crop((0,0,300,100))
    img_cropped.save('./data/levelup/users/levelup_bg_{}.jpg'.format(author_id))


  @commands.command(pass_context=True)
  async def level(self, ctx, mock = None):
    author_id = ctx.message.author.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute('SELECT * FROM Users WHERE id = {}'.format(author_id)).fetchone()

    username = ctx.message.author.name
    exp = user[2]
    max_exp = calculate_xp_for_lvl(user[3])
    level = int(user[3])
    s_placing = 1 + c.execute("SELECT (select count(*) from Users as u2 where u2.score > u1.score) FROM Users as u1 WHERE id = {}".format(author_id)).fetchone()[0]
    s_score = user[1]
    prestige = user[4]

    u_data = read_user_json(author_id)

    if mock and mock.isdigit():
        level = int(mock)
        username = "EXAMPLE"

    # Image stuff
    base = "./data/levelup/levelup_bg{}.jpg"
    if level >= 20:
        image_link = base.format('GE20')
    elif level >= 15:
        image_link = base.format('GE15')
    elif level >= 10:
        image_link = base.format('GE10')
    elif level >= 5:
        image_link = base.format('GE5')
    elif level >= 2:
        image_link = base.format('GE2')
    else:
        image_link = base.format('')

    custom_img = './data/levelup/users/levelup_bg_{}.jpg'.format(author_id)
    print(custom_img)
    if os.path.isfile(custom_img):
        image_link = custom_img

    th_size = 64, 64
    img = Image.open(image_link)
    fd = requests.get(ctx.message.author.avatar_url)
    i_f = io.BytesIO(fd.content)
    avatar = Image.open(i_f)
    draw = ImageDraw.Draw(img, 'RGBA')

    # Font stuff
    font = "./data/Roboto-Black.ttf"
    name_font = ImageFont.truetype(font, 16)
    exp_font = ImageFont.truetype(font, 8)
    level_label_font = ImageFont.truetype(font, 14)
    level_font = ImageFont.truetype('./data/Roboto-Bold.ttf', 30)
    placing_font = ImageFont.truetype(font, 11)
    prestige_font = ImageFont.truetype('./data/Roboto-Bold.ttf', 11)

    # Custom colors
    exp_color = tuple(u_data.get('xp', (190, 190, 200)))
    base_color = tuple(u_data.get('text', (60, 60, 70)))
    if prestige < 1:
      background_filler = (255, 255, 255)
    else:
      background_filler = tuple(u_data.get('background', (255, 255, 255)))

    # Background filler
    draw.rectangle([74,8,292,92], fill=background_filler + tuple([140]))

    # Avatar background filler
    draw.rectangle([27,15,97,85], fill=(0,0,0,50))

    # Avatar handling
    a_im = avatar.crop((0,0,128,128)).resize(th_size, Image.ANTIALIAS)
    img.paste(a_im, (30,18,94,82))

    # EXP Bar
    draw.rectangle([110,33,290,45], outline=exp_color)
    draw.rectangle([112,35,112+(290-112)*(exp/max_exp),43], fill=exp_color)

    # Text implementation
    exp_message = "EXP: {} / {}".format(exp, max_exp)
    w, h = draw.textsize(exp_message)
    draw.text((110, 15), username, base_color, font=name_font) # Username
    draw.text((125+(180-w)/2, 35), exp_message, base_color, font=exp_font) # EXP
    draw.text((110,48), "Level", base_color, font=level_label_font)

    w,h = draw.textsize(str(level))
    draw.text((110 if level > 9 else 118, 58), str(level), base_color, font=level_font)
    draw.rectangle([154,52,155,86], fill=exp_color)

    if prestige == 0:
      draw.text((162, 55), "Overall ranking", base_color, font=placing_font)
      draw.text((162, 70), "Total score", base_color, font=placing_font)

      draw.text((250, 55), "#{}".format(s_placing), base_color, font=placing_font)
      draw.text((250, 70), str(s_score), base_color, font=placing_font)
    else:
      draw.text((162, 50), "Prestige", base_color, font=prestige_font)
      draw.text((162, 62.5), "Overall ranking", base_color, font=placing_font)
      draw.text((162, 75), "Total score", base_color, font=placing_font)

      draw.text((250, 50), "{}".format(prestige), base_color, font=prestige_font)
      draw.text((250, 62.5), "#{}".format(s_placing), base_color, font=placing_font)
      draw.text((250, 75), str(s_score), base_color, font=placing_font)

    #draw.text((0,0),"Text Test",(255,255,255),font=font)
    img.save('./data/levelup/level-out.jpg')
    emoji = {'1': ':first_place:', '2': ':second_place:', '3': ':third_place:'}.get(str(s_placing), ':newspaper:')
    await self.bot.send_message(ctx.message.channel, "{} | **{}'s Level Card**".format(emoji, username))
    await self.bot.send_file(ctx.message.channel, './data/levelup/level-out.jpg')

    u_data = read_user_json(author_id)
    required_level = (1 + prestige // 5) * 25

    if level >= required_level:
      if required_level == 25:
        await self.bot.say('The **Grace of Light** lingers at your shoulder, eager to await your **prestige** (you are eligible to prestige with `?prestige`)')
      if required_level == 50:
        if not u_data.get('five_percent_medal', None):
          await self.bot.say('The **Grace of Light** acknowledges your power, but wishes to see you in combat...')
        else:
          await self.bot.say('The **Grace of Light** lingers at your shoulder, eager to await your **prestige** (you are eligible to prestige with `?prestige`)')
      if required_level >= 75:
        if not u_data.get('twenty_percent_medal', None):
          await self.bot.say('The **Grace of Light** wishes to bless you, but you lack the dedication to battle...')
        else:
          await self.bot.say('The **Grace of Light** lingers at your shoulder, eager to await your **prestige** (you are eligible to prestige with `?prestige`)')
      
def setup(bot):
  bot.add_cog(LevelUp(bot))