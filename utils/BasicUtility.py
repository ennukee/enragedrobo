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


# Source: http://code.activestate.com/recipes/415384-decimal-to-roman-numerals/
def decToRoman(i):
  if i <=0 or i >= 4000:
    return "INVALID"
  return dTR_help(i, "", [1000,900,500,400,100,90,50,40,10,9,5,4,1], ["M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"])

def dTR_help(i, s, decs, romans):
  if decs:
    if (i < decs[0]):
      return dTR_help(i,s,decs[1:],romans[1:])      
    else:
      return dTR_help(i-decs[0],s+romans[0],decs,romans)    
  else:
    return s

