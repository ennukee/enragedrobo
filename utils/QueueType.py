class QueueType:
	@staticmethod
	def meaning(i):
		__meanings = {
			0:   "Custom games",
			2:   "Normal 5v5 Blind Pick games",
			4:   "Ranked Solo 5v5 games",
			6:   "Ranked Premade 5v5 games", 
			7:   "Historical Summoner's Rift Coop vs AI games", 
			8:   "Normal 3v3 games",
			9:   "Ranked Premade 3v3 games", 
			14:  "Normal 5v5 Draft Pick games",
			16:  "Dominion 5v5 Blind Pick games",
			17:  "Dominion 5v5 Draft Pick games",
			25:  "Dominion Coop vs AI games",
			31:  "Summoner's Rift Coop vs AI Intro Bot games",
			32:  "Summoner's Rift Coop vs AI Beginner Bot games",
			33:  "Historical Summoner's Rift Coop vs AI Intermediate Bot games",
			41:  "Ranked Team 3v3 games",
			42:  "Ranked Team 5v5 games",
			52:  "Twisted Treeline Coop vs AI games",
			61:  "Team Builder games",
			65:  "ARAM games",
			70:  "One for All games",
			72:  "Snowdown Showdown 1v1 games",
			73:  "Snowdown Showdown 2v2 games",
			75:  "Summoner's Rift 6x6 Hexakill games",
			76:  "Ultra Rapid Fire games",
			83:  "Ultra Rapid Fire games played against AI games",
			91:  "Doom Bots Rank 1 games",
			92:  "Doom Bots Rank 2 games",
			93:  "Doom Bots Rank 5 games",
			96:  "Ascension games",
			98:  "Twisted Treeline 6x6 Hexakill games",
			100: "Butcher's Bridge games",
			300: "King Poro games",
			310: "Nemesis games",
			313: "Black Market Brawlers games",
			400: "Normal 5v5 Draft Pick games",
			410: "Ranked 5v5 Draft Pick games"
		}
		return __meanings[int(i)]

