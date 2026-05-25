from ursina import *
from game.entities.kenzo import Kenzo
from game.manager.resource import resourceManager
from game.manager.map import MapManager
from game.core.AI import AI

backgroundMap = resourceManager.picture("background/map/background")
platformTexture = resourceManager.picture("background/map/platform")

class Scene(Entity):
    def __init__(self):
        super().__init__()
        self.background = Entity(z=2, model='quad', texture=backgroundMap, scale= (30, 15), position=(0, 0))
        self.platformTexture = Entity(z=1.5, model='quad', texture=platformTexture, scale= (20, 12), position=(0, 0))
        self.platforms = [
            Entity(z=-1, name="solid", collider='box', model='quad', color="#2a2f26", visible=False, scale=(4.65, 1.75), position=(-3.25, -3.15)),
            Entity(z=-1, name="solid", collider='box', model='quad', color= "#2a2f26", visible=False,scale=(4.3, 1.75), position=(4.45, -3.15)),
            Entity(z=-1, name="platform", collider='box', model='quad', color= "#636226", visible=False,scale=(3.24, 0.65), position=(0.69, -2.6)),
            Entity(z=-1, name="solid", collider='box', model='quad', color='#2f2629', visible=False, scale=(2.2, 3), position=(-6.4, 2.2)),
            Entity(z=-1, name="solid",collider='box', model='quad', color='#2f2629', visible=False, scale=(6.4, 1), position=(0, 1.7)),
            Entity(z=-1, name="platform", collider='box', model='quad', color="#636226", visible=False, scale=(2.1, 0.65), position=(-4.25, 1.875)),
            Entity(z=-1, name="solid", collider='box', model='quad', color="#2f2629", visible=False, scale=(2.8, 1.15), position=(6.05, 3.9))
        ]
        self.player = Kenzo(position=(-2, 15, -1))
        self.team = []
        self.ai = AI(Kenzo(position=(2, 15, -1)), level = 3)
        self.enemy = [self.ai.player]
        self.play = MapManager(self)
    def update(self):
        self.ai.update()

