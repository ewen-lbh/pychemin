from os import path

GODSPEED_MODE = False
DEBUG_MODE = True
BASE_DIR = path.dirname(path.dirname(__file__))

STAT_NAMES = {
  'hp': "Vie",
  'speed': "Vitesse",
  'reputation': "Réputation",
  'food': "Niveau d'alimentation",
  'strength': "Force",
  'smart': "Intelligence",
  "name": "Nom"
}

NON_NUMERIC_STATS = ['name']
