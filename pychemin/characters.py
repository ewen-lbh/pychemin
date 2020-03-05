import toml
from colr import color
from termcolor import cprint, colored
from collections import namedtuple
from being import Being
from typing import List

class InvalidCharacterDefinition(Exception):
	"""Exception when a character definition is not correct"""

class Character(Being):
	def __init__(self, name, display_name, **kwargs):
		self.name = name
		self.display_name = display_name
		self.color = kwargs.get('color', '#fff')
		for prop, val in kwargs.items():
			setattr(self, prop, val)

def load_characters(raw_toml: str) -> List[Character]:
	parsed = toml.loads(raw_toml)
	for (var_name, attributes) in parsed.items():
		if 'name' not in attributes.keys():
			raise InvalidCharacterDefinition("Character %r has no name" % var_name)

		attributes['display_name'] = attributes['name']
		attributes['name'] = var_name
		yield Character(**attributes)
	