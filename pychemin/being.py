class Being:
  def __init__(self):
    pass
    
  def change_stat(self, stat, op, value):
    def rst(a, b):
      raise NotImplementedError("Stat resetting is not implemented yet.")
    ops = {
      'add': lambda a, b: a + b,
      'subtract': lambda a, b: a - b,
      'set': lambda a, b: b,
      'reset': rst,
      'multiply': lambda a, b: a * b
    }
    # On récupère la valeur actuelle pour la modifier
    val = getattr(self, stat)
    # On change la valeur
    setattr(self, stat, ops[op](val, value))
    # On récupère la nouvelle valeur
    new_val = getattr(self, stat)
    
    return {
      'stat_name': stat,
      'value': value,
      'old_value': val,
      'op': op,
      'new_value': new_val,
    }
