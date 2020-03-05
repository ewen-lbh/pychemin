from termcolor import cprint, colored
import os
from being import Being

class Player(Being):
    def __init__(self, name = "Ewen"):
        super().__init__()
        try:
            self.name = os.getlogin()
        except FileNotFoundError:
            self.name = name
        self.hp         = 100
        self.speed      = 100
        self.reputation = 0
        self.food       = 1
        self.smart      = 1/2
        self.strength   = 0
