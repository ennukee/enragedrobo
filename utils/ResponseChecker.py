class ResponseChecker:
	@staticmethod
	def is_good(i):
		return int(i) == 200

	@staticmethod
	def meaning(i):
		__meanings = {
			400: "Bad request",
			401: "You are not allowed to do that",
			403: "Forbidden request",
			404: "No summoner data found for any of the given inputs",
			429: "Rate limit exceeded, please wait and try again",
			500: "Internal server error occured",
			503: "Service unavailable"
		}
		return __meanings[int(i)]

