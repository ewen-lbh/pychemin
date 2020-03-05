import re, json
import debug, ui, characters
from player import Player
from parser import Parser
from constants import NON_NUMERIC_STATS
from exceptions import *
from characters import Character
from stats import Stat
from typing import List
from collections import namedtuple

class CurrentInput:
  def __init__(self, hint, actions_map, fallback, indent, current_case, required_cases):
    self.hint = hint
    self.actions_map = actions_map
    self.fallback = fallback
    self.indent = indent
    self.current_case = current_case
    self.required_cases = required_cases
    
class Walker:
  def __init__(self, directives, characters, stats, act=0, chapter=0):
    self.directives = directives
    self.characters = characters
    self.stats = stats
    self.line = 0
    self.act = act
    self.chapter = chapter
    self.player = Player()
    self.context = {
      'name': self.player.name
    }
    self.collecting_input = False
    self.collecting_input_cases = False
    self.collecting_input_fallback = False
    self.current_input = CurrentInput(
      hint="",
      actions_map={},
      required_cases=[],
      fallback=[],
      indent=0,
      current_case=None
    )
  
  def walk(self, directives = None):
    debug.log(f'Running with directives: {self.directives!r}')
    for (indent_depth, directive) in (directives or self.directives):
      self.line += 1 #TODO: get line number from first token
      type = directive.data
      nodes = directive.children
      debug.log(f'@{self.line:0>3} {type}[{indent_depth}]: {nodes!r}')
      if self.collecting_input:
        debug.log(f'self.collecting_input')
        if self.current_input.indent + 1 == indent_depth:
          debug.log(f'self.current_input.indent + 1 == indent_depth')
          if self.collecting_input_fallback:
            debug.log(f'self.collecting_input_fallback')
            self.add_to_fallback_case((indent_depth, directive))
          else:
            self.add_to_input_case((indent_depth, directive))
        else:
          if type.startswith('input'):
            self.dispatch(type, nodes)
          else:
            self.execute_input()
            self.dispatch(type, nodes)
      else:
        self.dispatch(type, nodes)
    
  def dispatch(self, type, nodes):
    if type.startswith('input'):
      self.collecting_input = True
    if type in ('input', 'input_required', 'input_fallback'):
      self.handle_input(type, nodes)
    else:
      try:
        getattr(self, f'handle_{type}')(type, nodes)
      except AttributeError:
        raise NotImplementedError(f"Directive {type!r} not implemented")
    
  def handle_comment(self, type, nodes):
    pass
  
  def handle_execute_code(self, type, nodes):
    try:
      eval(nodes[0].value)
    except Exception as err:
      raise RuntimeError(f'at line {nodes[0].line}: {err}')
  
  def handle_narrator_line(self, type, nodes):
    ui.narrator(nodes[0].value)
  
  def handle_char_line(self, type, nodes):
    character_name = nodes[0].value
    text = nodes[1].value
    
    character_name = character_name if character_name != '???' else 'Unknown'
    text = self.substiute(text)
    character = self._get_character(character_name)
    
    ui.say(character, text)
  
  def handle_new_act(self, type, nodes):
    self.act += 1
    ui.act(self.act, nodes[0].value)
  
  def handle_new_chapter(self, type, nodes):
    self.chapter += 1
    ui.chapter(self.chapter, nodes[0].value)
    
  def handle_stat_change(self, type, nodes):
    debug.log(f'type={type!r}')
    debug.log(f'nodes={nodes!r}')
    if len(nodes) == 2:
      target = self.player
      stat_name = nodes[0].value
      operation = nodes[1]
    else:
      target = self._get_character(nodes[0].value)
      stat_name = nodes[1].value
      operation = nodes[2]
    operator = operation.data
    if stat_name not in NON_NUMERIC_STATS:
      value = operation.children[0].value
      value = float(value)
    else:
      interpolation_key = operation.children[0].children[1].value
      value = self.context[interpolation_key]
    stat_change = target.change_stat(stat_name, operator, value)
    ui.stat_change(**stat_change)
  
  def _get_character(self, name: str) -> Character:
    try:
      return [ c for c in self.characters if c.name == name ][0]
    except IndexError:
      raise PyCheminRuntimeError(f"No character named {name!r}")
    
  def handle_load_file(self, type, nodes):
    file = nodes[0].value
    file = file.replace(' ', '_')
    file += '.pychemin'
    file = 'story/' + file
    file = open(file, 'r').read()
    directives = Parser().parse(file)
    Walker(directives, self.act, self.chapter).walk()
    
  def execute_input(self):
    self.collecting_input = False
    fallback = self._make_walk_func(self.current_input.fallback)
    answer = ui.ask(
      choices=self._get_input_choices(),
      # ask_again=self.current_input.
      restrict_to_choices=not fallback,
      hint=self.current_input.hint,
      error_callback=fallback
    )
    self.context['answer'] = answer
    for case, directives in self.current_input.actions_map.items():
      debug.log(f'For case {case!r}: {directives!r}')
      if answer in json.loads(case) or answer in self.current_input.required_cases:
        if not directives:
          debug.log(f'[WARN] No directives for case {case!r}')
        else:
          self._make_walk_func(directives)()
    
    
  def _get_input_choices(self):
    return [json.loads(k) for k in self.current_input.actions_map.keys()]
    
  
  def _make_walk_func(self, directives):
    if not directives:
      return None
    def _func():
      self.walk(directives)
    return _func
  
  def handle_input(self, type, nodes):
    input_type = type.replace('input_', '')
    self.collecting_input = True
    self.collecting_input_fallback = False
    if input_type == 'fallback':
      self.collecting_input_fallback = True
    elif input_type == 'fallback_and_continue':
      self.collecting_input_fallback = True
    elif input_type == 'required':
      self.add_input_case(nodes[0].value, required=True)
    else:
      self.add_input_case(nodes[0].value)
  
  def handle_input_hint(self, type, nodes):
    self.current_input.hint = nodes[0].value
  
  def add_input_case(self, choices, required=False):
    choices = choices.split(',')
    choices = [ c.strip() for c in choices ]
    choices = [ self.substiute(c) for c in choices ]
    choices = json.dumps(choices)
    debug.log(f'Adding input case {choices}')
    self.current_input.current_case = choices
    self.current_input.actions_map[choices] = []
  
  def add_to_input_case(self, directive):
    debug.log(f'Adding {directive} to case {self.current_input.current_case}')
    self.current_input.actions_map[self.current_input.current_case].append(directive)

  def add_to_fallback_case(self, directive):
    debug.log(f'Adding {directive} to fallback case')
    self.current_input.fallback.append(directive)

  def substiute(self, text):
    matches = re.finditer(r'#([\w_]+) ', text)
    if not matches: return text
    for m in matches:
      replace_with = str(self.context[m.group(1)]) + ' '
      debug.log(f'Replacing {m.group(0)} with {replace_with!r}')
      text.replace(m.group(0), replace_with)
    return text
