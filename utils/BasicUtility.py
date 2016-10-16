import json
import os

def load_api_key(name):
  with open('data/apikeys.json') as f:
    try:
      return json.load(f)[name]
    except KeyError as e:
      return None

def load_credentials():
  with open('data/login.json') as f:
    return json.load(f)

def admins():
  with open('data/admins.json') as f:
    j = json.load(f)
    return [x for x in j if j[x]==1]

def custom_command_list():
  return [x[:-5] for x in os.listdir('./data/custom_commands')]

def clean(i):
  return i.lower().replace(' ','')

def calculate_xp_for_lvl(level):
  return int(sum(i+300*pow(2, i/7) for i in range(1,level+1))/4)

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