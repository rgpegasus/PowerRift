# Créer la fenetre de jeu
from ursina import *
from .variables import Variables
from game.manager.page import PageManager

class Engine:
    def __init__(self):
        self.app = Ursina(title="Power Rift", borderless=True, fullscreen=False) 
        window.size = Variables.WINDOW_SIZE
        window.position = (0,0)
        window.color = color.gray

        PageManager.load("menu")

    def run(self):
        self.app.run()

engine = Engine()
