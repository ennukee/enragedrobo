import datetime
import sys

class BotConstants:
  def __init__(self):
    self.__ingame = False
    self.__gamechannel = None
    self.__gameserver = None
    self.__gamestarter = None
    self.__afks = {}
    self.id = '183740131562225665'
    self.owner_id = '126122455248011265'
    self.bug_reports_channel_id = '200090197885452288'
    self.start_time = datetime.datetime.now()
    self.initial_extensions = [
                               #'modules.trivia',
                                'modules.leagueapi',
                                'modules.botconfig',
                                'modules.dbd',
                                'modules.cipher',
                                'modules.cmd',
                                'modules.misc',
                                'modules.level'
                              ]
    self.last_flip = None
    self.message_xp = 5
    self.last_message = {}
    self.levelup = {'json_path': './data/levelup/users/{}.json'}

  def set_private_channel(self, channel):
    self.private_channel = channel

  def toggle_ingame(self):
    self.__ingame = not self.__ingame

  def ingame(self):
    return self.__ingame

  def is_afk(self, user):
    return user in self.__afks

  def afk_reason(self, user):
    if self.is_afk(user):
      return self.__afks[user]
    else:
      return ""

  def add_afk(self, user, message):
    try:
      self.__afks[user] = message
      return 1
    except Exception as e:
      return 0

  def remove_afk(self, user):
    if self.is_afk(user):
      try:
        self.__afks.pop(user)
        return 1
      except Exception as e:
        return 0

  def set_gamedata(self, channel, server, starter):
    self.__gamechannel = channel
    self.__gameserver = server
    self.__gamestarter = starter

  def get_gamedata(self):
    return [self.__gamechannel, self.__gameserver, self.__gamestarter.id]

  def get_start(self):
    return self.start_time

  def set_last_flip(self, flip):
    self.last_flip = flip

  def get_last_flip(self):
    return self.last_flip

botv = BotConstants()
