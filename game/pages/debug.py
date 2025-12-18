from ursina import *
from game.entities.demon import Demon
from game.manager.resource import resourceManager
backgroundMap = resourceManager.picture("background/map/test")
class Scene(Entity):
    def __init__(self):
        super().__init__()
        self.player = Demon( scale=(0.6, 0.75), position=(-2, 10))
        self.ground = Entity(z=-1, name="solid", collider='box', model='quad', color= '#5d5720', scale=(20, 2), position=(0, -1))
        self.plat_left = Entity(z=-1, name="solid", texture=backgroundMap, collider='box', model='quad', color='#2f2629', scale=(3, 100), position=(-3, 50))
        self.plat_right = Entity(z=-1, name="solid",  texture=backgroundMap, collider='box', model='quad', color='#2f2629', scale=(3, 100), position=(3, 50))
        self.texte = Text(text=int(self.player.y), parent=camera.ui, position=(0, 0.25), color=color.black)

        camera.orthographic = True
        camera.fov = 10
        self.mainMusic = resourceManager.music("main")
        if self.mainMusic:
            self.mainMusic.play()
    def update(self):
        if self.player.x > -5 and self.player.x < 5:
            camera.x = self.player.x
        camera.y = self.player.y
        self.texte.text=int(self.player.y)
        if self.player.y <= -20 or self.player.x <= -5 and self.player.x >= 5:
            self.player.position=(0, 10)
            self.player.velocity_y = 0