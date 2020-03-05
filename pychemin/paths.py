from constants import BASE_DIR
from os import path

GRAMMAR = path.join(BASE_DIR, 'pychemin', 'grammar.lark')
STORY_DIR = path.join(BASE_DIR, 'story')
STORY_ENTRY_POINT = path.join(STORY_DIR, 'story.pychemin')
