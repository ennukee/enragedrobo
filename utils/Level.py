# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord  # Overall discord library
import datetime, re # Datetime and regular expression libraries
import json, asyncio # json / asyncio libraries
import copy
import logging # Debug logging
import sys, os # Lower-level operations libraries
import requests # API queries
import textwrap
import urllib.request # Downloading
import random # Random (RNG)
from time import sleep # For delays
from collections import defaultdict
import numpy as np # Advanced number/set arithmetic
from _thread import *
from bs4 import BeautifulSoup

import sqlite3
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# - - My libraries - - #
import checks # Ensures various predefined conditions are met
from utils import imageloader # Image downloader
from utils.BasicUtility import * # Basic utility functions

def calculate_xp_for_lvl(level):
  return int(sum(i+300*pow(2, i/7) for i in range(1,level+1))/4)

def calculate_level_gain(cur_exp, level):
	gain = 0
	while cur_exp > calculate_xp_for_lvl(level):
		cur_exp -= calculate_xp_for_lvl(level)
		gain += 1
	return cur_exp, gain

def congratulate_level(bot, level, gain, message):
  if gain < 1:
		return
	await bot.send_message(message.channel, "**:up: | Level Up!**")
  generate_level_up_image(level, message.author.avatar_url)
  await bot.send_file(message.channel, './data/levelup/level_up.jpg')
  if level == 5 or level - 5 < gain:
  	await bot.send_message(message.channel, "**Level 5 Perks**\nUnlocked `?gamble <amt>` and `?train`")
  elif level == 25 or level - 25 < gain:
  	await bot.send_message(message.channel, "**Level 25 Perks**\nUnlocked `?setbg <link>`!")

def generate_level_up_image(level, url):
  from PIL import Image
  from PIL import ImageFont
  from PIL import ImageDraw
  import io
  import requests

  # Image stuff
  th_size = 50, 50
  img = Image.open("./data/levelup/levelup_bg2.jpg")
  fd = requests.get(url)
  i_f = io.BytesIO(fd.content)
  avatar = Image.open(i_f)
  draw = ImageDraw.Draw(img, 'RGBA')

  # Font stuff
  font = "./data/Roboto-Black.ttf"
  name_font = ImageFont.truetype(font, 12)
  level_font = ImageFont.truetype(font, 26)
  base_color = (60, 60, 70)
  exp_color = (190, 190, 200)

  # # Avatar background filler
  draw.rectangle([13,8,67,62], fill=(0,0,0,50))

  # # Avatar handling
  a_im = avatar.crop((0,0,128,128)).resize(th_size, Image.ANTIALIAS)
  img.paste(a_im, (15,10,65,60))

  # Text implementation
  draw.text((15, 63), "Level Up!", base_color, font=name_font)
  draw.text((25 if level > 9 else 33,72), str(level), base_color, font=level_font)

  img.save('./data/levelup/level_up.jpg')