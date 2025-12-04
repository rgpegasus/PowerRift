# Exemple de trame de code pour créer une entité 
from ursina import *
from game.manager.input import inputManager
from game.core.variables import Variables

class Exemple(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model="quad",
            texture="white_cube",
            scale=(1, 1),
            collider="box",
            **kwargs
        )
        self.speed = Variables.PLAYER_SPEED
        self.hp = 100

    def update(self):
        self.move()

    def move(self):
        if inputManager.pressed("left"):
            self.x = self.x - time.dt * self.speed
        if inputManager.pressed("right"):
            self.x = self.x + time.dt * self.speed