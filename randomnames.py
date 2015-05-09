from random import choice

class RandomNames:
	def __init__(self, adjectives="adjectives.txt", nouns="nouns.txt"):
		self.adjectives = open(adjectives).read().splitlines()
		self.nouns = open(nouns).read().splitlines()

	def getRandomName(self):
		return choice(self.adjectives) + ' ' + choice(self.nouns)
