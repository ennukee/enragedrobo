class BotConstants:
	def __init__(self):
		self.__ingame = False
		self.__gamechannel = None
		self.__gameserver = None
		self.__gamestarter = None
		self.id = '133745418797318144'
	def toggle_ingame(self):
		self.__ingame = not self.__ingame
	def ingame(self):
		return self.__ingame
	def set_gamedata(self, channel, server, starter):
		self.__gamechannel = channel
		self.__gameserver = server
		self.__gamestarter = starter
	def get_gamedata(self):
		return [self.__gamechannel, self.__gameserver, self.__gamestarter.id]


botv = BotConstants()
