import urllib.request
import re

regex = re.compile(
  r'^(?:http|ftp)s?://' # http:// or https://
  r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
  r'localhost|' #localhost...
  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
  r'(?::\d+)?' # optional port
  r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def load_image(url):
	if regex.match(url) == None:
		raise ValueError("The provided url was improper by Django standards", "url")
	urllib.request.urlretrieve(url, "avatar_folder/avatar.jpg")

def load_background(url, id):
	if regex.match(url) == None:
		raise ValueError("The provided url was improper by Django standards", "url")
	urllib.request.urlretrieve(url, "data/levelup/users/levelup_bg_{}.jpg".format(id))

def load_splash_art(champ, skin_num, valid):
	if champ in valid:
		try:
			url = 'http://ddragon.leagueoflegends.com/cdn/img/champion/loading/{}_{}.jpg'.format(champ, skin_num)
			urllib.request.urlretrieve(url, 'data/league/current_splash.jpg')
		except Exception as e:
			raise e
	else:
		raise ValueError('That champion is invalid')

