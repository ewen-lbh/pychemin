from lark import Lark
import paths

class Parser:
  def __init__(self):
    grammar = open(paths.GRAMMAR, 'r').read()
    self.lark = Lark(grammar, start='dialog', maybe_placeholders=True)

  def parse(self, story):
    self.parsed = self.lark.parse(story)
    self.clean()
    self.treat()
    return self.parsed
  
  def clean(self):
    self._no_blank_lines()
    self._no_comments()
    
  def treat(self):
    self._add_indent_levels()
    
  def _no_blank_lines(self):
    self.parsed = [ d for d in self.parsed.children if hasattr(d, 'data') ]
  
  def _no_comments(self):
    self.parsed = [ d for d in self.parsed if d.data != 'comment' ]
  
  def _add_indent_levels(self):
    with_indents = []
    for line in self.parsed:
      indent = len([c for c in line.children if c.data == 'indent'])
      directive = [c for c in line.children if c.data != 'indent'][0]  # There should be at most one directive per line (and 0+ indent tokens)
      with_indents.append((indent, directive))
    self.parsed = with_indents
