import re
import urllib.request
from bs4 import BeautifulSoup
import cgi

def MAL_anime_info(url):
  # I really wish the MAL API wasn't total trash, I really do. This is ugly. Don't mimic this code.

  # To ensure the link is safe to use, we need to make sure the link doesn't include the potentially-ascii-filled ending
  # A split link should look like this:
  # ['http:', '', ''myanimelist.net', 'anime', (some number), (some text)]
  split_url = url.split('/') 
  url = '/'.join(split_url[0:5]) # Up to, but not including, the 5th index (aka some text)

  indiv_output = [None] * 5
  page = urllib.request.urlopen(url)
  soup = BeautifulSoup(page.read().decode(), 'html.parser')

  indiv_output[0] = '**{}**'.format(soup.find('span', {'itemprop': 'name'}).text.strip())
  indiv_output[1] = 'Link: <{}>'.format(url)
  indiv_output[2] = '**Episodes**: {}'.format(soup.find('span', text='Episodes:').next_sibling.strip())
  indiv_output[3] = '**Status**: {}'.format(soup.find('span', text='Status:').next_sibling.strip())

  if indiv_output[3] != 'Not yet aired':
    rating_value = soup.find('span', {'itemprop': 'ratingValue'}).text.strip()
    rating_count = soup.find('span', {'itemprop': 'ratingCount'}).text.strip()
    indiv_output[4] = '**Rating**: {} (by {} users)'.format(rating_value, rating_count)
  else:
    indiv_output[4] = '**Rating**: None (unaired)'

  return indiv_output

def MAL_anime_search(query):
  indiv_output = [None] * 2
  query = cgi.escape(query.replace(' ','%20')).encode('ascii', 'xmlcharrefreplace')
  page = urllib.request.urlopen('http://myanimelist.net/anime.php?q={}'.format(query))
  soup = BeautifulSoup(page.read().decode(), 'html.parser')

  return soup.find_all('td', class_="bgColor0")[1].a

def MAL_manga_info(url):
  # I really wish the MAL API wasn't total trash, I really do. This is ugly. Don't mimic this code.

  # To ensure the link is safe to use, we need to make sure the link doesn't include the potentially-ascii-filled ending
  # A split link should look like this:
  # ['http:', '', ''myanimelist.net', 'manga', (some number), (some text)]
  split_url = url.split('/') 
  url = '/'.join(split_url[0:5]) # Up to, but not including, the 5th index (aka some text)

  indiv_output = [None] * 6
  page = urllib.request.urlopen(url)
  soup = BeautifulSoup(page.read().decode(), 'html.parser')

  indiv_output[0] = '**{}**'.format(soup.find('span', {'itemprop': 'name'}).text.strip())
  indiv_output[1] = 'Link: <{}>'.format(url)
  indiv_output[2] = '**Volumes**: {}'.format(soup.find('span', text='Volumes:').next_sibling.strip())
  indiv_output[3] = '**Chapters**: {}'.format(soup.find('span', text='Chapters:').next_sibling.strip())
  indiv_output[4] = '**Status**: {}'.format(soup.find('span', text='Status:').next_sibling.strip())

  if indiv_output[4] != 'Not yet published':
    rating_value = soup.find('span', {'itemprop': 'ratingValue'}).text.strip()
    rating_count = soup.find('span', {'itemprop': 'ratingCount'}).text.strip()
    indiv_output[5] = '**Rating**: {} (by {} users)'.format(rating_value, rating_count)
  else:
    indiv_output[5] = '**Rating**: None (unaired)'

  return indiv_output

def MAL_manga_search(query):
  indiv_output = [None] * 2
  query = cgi.escape(query.replace(' ','%20')).encode('ascii', 'xmlcharrefreplace')
  page = urllib.request.urlopen('http://myanimelist.net/manga.php?q={}'.format(query))
  soup = BeautifulSoup(page.read().decode(), 'html.parser')

  return soup.find_all('td', class_="bgColor0")[1].a