from typing import List
import debug
import toml

class ValidationError(Exception):
  """When a stat value was not validated"""
class InvalidStatDefinition(Exception):
  """When a stat has not been defined properly"""

class Stat:
  def __init__(self, name, display_name = None, domain="0 to +oo", type="integer"):
    self.name = name
    self.display_name = display_name
    self.domain = tuple(domain.split(' to '))
    self.type = {
      "float": float,
      "string": str,
      "integer": int
    }[type]
  
  def validate_value(self, value):
    if type(value) is not self.type:
      raise ValidationError("Value %r has type %r, which doesn't match %r's, %r." % (value, type(value), self.__class__, ))
          
    
def load_stats(raw_toml: str) -> List[Stat]:
  for name, attributes in toml.loads(raw_toml):
    yield Stat(name, **attributes)
