# Exemple de menu simple
from ursina import *
from game.manager.page import PageManager

class Scene(Entity):
    def __init__(self):
        super().__init__()
        Text(
            "MENU PRINCIPAL", 
            x=-0.1, 
            y = 0.05
        )
        Button(
            "Jouer", 
            y=-0.05, 
            scale_x = 0.25, 
            scale_y = 0.035, 
            on_click=lambda: PageManager.load("test")
        )
