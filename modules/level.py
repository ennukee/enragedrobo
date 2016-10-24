# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord # Overall discord library
import json, asyncio # json / asyncio libraries
import sys, os # Lower-level operations libraries
import urllib.request # Downloading
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
from utils import imageloader # Image downloader
from utils.BasicUtility import *
from utils.BotConstants import *

class LevelUp:
  """Holds all the logic for the bot's leveling system"""
  def __init__(self, bot):
    self.bot = bot
    self.last_trained = {}
    self.last_saved = {}

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

    new_exp = exp
    new_score = s_score

    SAVE_TIME = 7200

    if level < 5:
        await self.bot.say("You need to be **level 5** to use this!")
        return
    elif exp < offer:
        await self.bot.say('You do not have that much XP to offer')
        return
    elif offer < max_exp / 8:
        await self.bot.say('You need to offer at least one eighth of your level ({})'.format(max_exp / 8))
        return

    # Chances
    # 40.0% -> Lose XP
    # 30.0% -> Keep XP
    # 12.5% -> Double XP
    # 5.00% -> Instant level
    # 10.0% -> Reset training
    # 2.50% -> Boss fight

    options = ['lose', 'keep', 'double', 'level', 'reset_training', 'boss'] 
    result = 'boss'#np.random.choice(options, p = [0.4, 0.3, 0.125, 0.05, 0.1, 0.025])

    if result == 'lose':
        recently_saved = self.last_saved.get(author_id, None)
        time_since_last = (datetime.datetime.now() - recently_saved).total_seconds() if recently_saved else 100000

        if time_since_last > SAVE_TIME:
            self.last_saved[author_id] = datetime.datetime.now()
            await self.bot.say('You would have lost offering, but the Grace of Light has saved it. You cannot be saved for another two hours.')
        else:
            await self.bot.say('Unfortunately, the black magic steals away part of you. You lose the offering.')
            new_exp -= offer
            new_score -= offer
    elif result == 'keep':
        await self.bot.say('You feel the black magic simply pass by.')
    elif result == 'double':
        new_exp += offer
        new_score += offer
        await self.bot.say('You feel the black magic grace you with a gift. You gain back your offering and more.')
    elif result == 'level':
        await self.bot.say('The black magic courses through you. You gain a level.')
        new_exp += (max_exp - exp)
        new_score += (max_exp - exp)
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
            chosen_boss = 'Chromus'#random.choice(bosses)
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
            events.append('**EXP Gained**: {}'.format(level * 10 * correct_moves))
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

    if level < 5:
        await self.bot.say("You need to be **level 5** to use this!")
        return

    last_session = self.last_trained.get(author_id, None)
    time_since_last = (datetime.datetime.now() - last_session).total_seconds() if last_session else 100000

    WAIT_TIME = 3600

    if not last_session or time_since_last > WAIT_TIME:
        self.last_trained[author_id] = datetime.datetime.now()

        events = ['You begin training...\n']

        exp_gain = level * 12
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
                exp_for_winning = m_level * m_mult * global_multiplier
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

    if mock and mock.isdigit():
        level = int(mock)
        username = "EXAMPLE"

    # Image stuff
    base = "./data/levelup/levelup_bg{}.jpg"
    if level >= 25:
        image_link = base.format('GE25')
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
    base_color = (60, 60, 70)
    exp_color = (190, 190, 200)

    # Background filler
    draw.rectangle([74,8,292,92], fill=(255, 255, 255, 120))

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

    draw.text((162, 55), "Overall ranking", base_color, font=placing_font)
    draw.text((162, 70), "Total score", base_color, font=placing_font)

    draw.text((250, 55), "#{}".format(s_placing), base_color, font=placing_font)
    draw.text((250, 70), str(s_score), base_color, font=placing_font)

    #draw.text((0,0),"Text Test",(255,255,255),font=font)
    img.save('./data/levelup/level-out.jpg')
    emoji = {'1': ':first_place:', '2': ':second_place:', '3': ':third_place:'}.get(str(s_placing), ':newspaper:')
    await self.bot.send_message(ctx.message.channel, "{} | **{}'s Level Card**".format(emoji, username))
    await self.bot.send_file(ctx.message.channel, './data/levelup/level-out.jpg')

      
def setup(bot):
  bot.add_cog(LevelUp(bot))