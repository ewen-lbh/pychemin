from sys import argv
import paths
import debug
from walker import Walker
from parser import Parser
from characters import load_characters
from stats import load_stats

class Game:
	def __init__(self, story: str, characters: str, stats: str):
		self.story = str(story)
		self.characters = load_characters(characters)
		self.stats = load_stats(stats)

	def start(self):
		debug.log(f"Starting parser on {self.story!r}")
		directives = Parser().parse(self.story)
		Walker(directives, characters=self.characters, stats=self.stats).walk()
