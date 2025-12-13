from ursina import *
from game.entities.exemple import Exemple
from game.manager.resource import resourceManager
backgroundMap = resourceManager.picture("background/map/test")
class Scene(Entity):
    def __init__(self):
        super().__init__()
        self.player = Exemple(scale=(0.6, 0.75), position=(0, 10))
        self.background = Entity(z=2, model='quad', texture=backgroundMap, scale= (30, 15), position=(0, 0))
        self.ground = Entity(z=-1, name="solid", collider='box', model='quad', color= "#2a2f26", scale=(8.25, 2.5), position=(0.25, -2.25))
        self.plat_left = Entity(z=-1, name="solid", collider='box', model='quad', color='#2f2629', scale=(1.5, 3), position=(-5.5, 1.5))
        self.plat_topr = Entity(z=-1, name="solid",collider='box', model='quad', color='#2f2629', scale=(2.75, 0.65), position=(2.25, 1.5))
        self.plat_topm = Entity(z=1, name="platform", collider='box', model='quad', color="#636226", scale=(1.74, 0.15), position=(0, 1.75))
        self.plat_topl = Entity(z=-1, name="solid",collider='box', model='quad', color='#2f2629', scale=(2.75, 0.65), position=(-2.25, 1.5))
        self.plat_right = Entity(z=-1, name="solid", collider='box', model='quad', color="#2f2629", scale=(2, 1.5), position=(6, 3.5))

        camera.orthographic = True
        camera.fov = 10

    def update(self):
        if self.player.x > -5 and self.player.x < 5:
            camera.x = self.player.x
        if self.player.y > -2.5 and self.player.y <= 2.5:
            camera.y = self.player.y
        elif self.player.y > 2.5:
            camera.y = 2.5
        if self.player.y <= -20 or self.player.y >= 20 or self.player.x <= -5 and self.player.x >= 5:
            self.player.position=(0, 10)
            self.player.velocity_y = 0