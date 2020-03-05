"""A minimal language to describe interactive, terminal-based text adventure games

Usage:
	pychemin (- | STORY-FILE) (-c CHARACTERS-FILE -s STATS-FILE) [--godspeed]
	pychemin (-h | --help | --version)

Options:
	-c --characters=FILE		Provide the file defining the characters [default: characters.toml]
	-s --stats=FILE					Provide the file defining the stats [default: stats.toml]
	-h --help								Show this help
	--version								Show PyChemin's version
	--godspeed							Print all text instantly
	-D --debug							Show debug information
"""
import os, sys
from docopt import docopt
from main import Game
import debug
def run():
	args = docopt(__doc__)
	debug.log(args)
	if args['-']:
		story = sys.stdin.read()
	else:
		story = open(args['STORY-FILE'], 'r').read()
	characters = open(args['CHARACTERS-FILE'], 'r').read()
	stats = open(args['STATS-FILE'], 'r').read()
	game = Game(story, characters, stats).start()
	
if __name__ == "__main__":
	run()
