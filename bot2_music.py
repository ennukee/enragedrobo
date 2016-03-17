# - - External Libraries - - #
from discord.ext import commands # Command interface
import discord  # Overall discord library
import datetime, re # Datetime and regular expression libraries
import json, asyncio # json / asyncio libraries
import logging # Debug logging
import sys, os # Lower-level operations libraries
from time import sleep # For delays
import pafy # Simplistic youtube link to audio file conversion

# - - - - - - - - - - - - - - - - - - - - - -  #
# - - Bot commands / generic library usage - - #
# - - - - - - - - - - - - - - - - - - - - - -  #
# Codebase credit to Danny (discordpy creator) #

if not discord.opus.is_loaded():
    discord.opus.load_opus('data/opus.dll')

class VoiceEntry:
    def __init__(self, message, song):
        self.requester = message.author
        self.channel = message.channel
        self.song = song

class Bot(discord.Client):
  def __init__(self):
    super().__init__()
    self.songs = asyncio.Queue()
    self.play_next_song = asyncio.Event()
    self.starter = None
    self.player = None
    self.current = None

  def toggle_next_song(self):
    self.loop.call_soon_threadsafe(self.play_next_song.set)

  def can_control_song(self, author):
    return author == self.starter or (self.current is not None and author == self.current.requester)

  def is_playing(self):
    return self.player is not None and self.player.is_playing()

  async def on_message(self, message):
    if message.author == self.user:
      return

    if message.channel.is_private:
      await self.send_message(message.channel, 'You cannot use this bot in private messages.')

    elif message.content == ';end':
      sys.exit()
    elif message.content.startswith(';join'):
      if self.is_voice_connected():
        await self.send_message(message.channel, "Sorry, I'm already connected to a channel!")
        return
      channel = message.author.voice_channel
      if channel is None:
        await self.send_message(message.channel, "You are not connected to a voice channel!")
      else:
        await self.join_voice_channel(channel)
        self.starter = message.author

    elif message.content.startswith(';leave'):
      if not self.can_control_song(message.author):
        return
      self.starter = None
      await self.voice.disconnect()

    elif message.content.startswith(';pause'):
      if not self.can_control_song(message.author):
        fmt = 'Only the requester ({0.current.requester}) can control this song'
        await self.send_message(message.channel, fmt.format(self))
      elif self.player.is_playing():
        self.player.pause()

    elif message.content.startswith(';resume'):
      if not self.can_control_song(message.author):
        fmt = 'Only the requester ({0.current.requester}) can control this song'
        await self.send_message(message.channel, fmt.format(self))
      elif self.player is not None and not self.is_playing():
        self.player.resume()

    elif message.content.startswith(';skip'):
      if not self.can_control_song(message.author):
        fmt = 'Only the requester ({0.current.requester}) can control this song'
        await self.send_message(message.channel, fmt.format(self))
      if self.player is not None and self.is_playing():
        self.toggle_next_song

    elif message.content.startswith(';next'):
      url = message.content[5:].strip()
      regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
      if regex.match(url) == None:
        await self.send_message(message.channel, "The URL you provided does not match Django standards (please use the full link!)")
        return
      
      video = pafy.new(url)
      filepath = "data/music/{}.webm".format(video.title)
      if(video.viewcount < 2500 or video.likes / video.dislikes < 10):
        await self.send_message(message.channel, "Sorry, that video has too little views / poor rating to be trusted.")
      elif(video.length > 300):
        await self.send_message(message.channel, "Max length of a request is **5 minutes**, please!")
      else:
        await self.send_message(message.channel, "Currently downloading the requested song...")
        try:
          os.remove(filepath)
        except OSError:
          pass
        video.audiostreams[0].download(filepath="data/music")
        await self.songs.put(VoiceEntry(message, filepath))
        await self.send_message(message.channel, 'Successfully registered **{}**'.format(video.title))
        await self.send_message(message.channel, "Download processed. Thank you.")

    elif message.content.startswith(';play'):
      if self.player is not None and self.player.is_playing():
        await self.send_message(message.channel, 'Already playing a song')
        return
      while True:
        if not self.is_voice_connected():
            await self.send_message(message.channel, 'Not connected to a voice channel')
            return
        self.play_next_song.clear()
        self.current = await self.songs.get()
        self.player = self.voice.create_ffmpeg_player(self.current.song, after=self.toggle_next_song)
        self.player.start()
        fmt = 'Playing song "{0.song}" from {0.requester}'
        await self.send_message(self.current.channel, fmt.format(self.current))
        await self.play_next_song.wait()

  async def on_ready(self):
    print('Logged in as')
    print(self.user.name)
    print(self.user.id)
    print('------')

# - - Program run section - - #

def load_credentials():
  with open('data/login.json') as f:
    return json.load(f)

if __name__ == '__main__':
  login = load_credentials()
  bot = Bot()
  bot.run(login['email'], login['password'])
  