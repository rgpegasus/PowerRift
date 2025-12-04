# Exemple de jeu simple
from ursina import *
from game.entities.exemple import Exemple

class Scene(Entity):
    def __init__(self):
        super().__init__()
        self.player = Exemple()
