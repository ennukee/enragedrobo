class MapNames:
	@staticmethod
	def meaning(i):
		__meanings = {
			1:	"Summoner's Rift (Original Summer Variant)",
			2:	"Summoner's Rift (Original Autumn Variant)",
			3:	"The Proving Grounds (Tutorial Map)",
			4:	"Twisted Treeline (Original Version)",
			8:	"The Crystal Scar (Dominion Map)",
			10:	"Twisted Treeline (Current Version)",
			11:	"Summoner's Rift (Current Version)",
			12:	"Howling Abyss (ARAM Map)",
			14:	"Butcher's Bridge (ARAM Map)"
		}
		return __meanings[int(i)]


