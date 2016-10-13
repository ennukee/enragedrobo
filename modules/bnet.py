from utils.BasicUtility import *

class BattleNet:
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def refreshAH(self):
		print('lul')


def setup(bot):
	bot.add_cog(BattleNet(bot))