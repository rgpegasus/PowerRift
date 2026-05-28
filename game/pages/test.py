from ursina import *
from game.entities.demon import Demon
from game.entities.kenzo import Kenzo
from game.manager.resource import resourceManager
from game.core.AI import AI
backgroundMap = resourceManager.picture("background/map/background")
platformMap = resourceManager.picture("background/map/platform")

class Scene(Entity):
    def __init__(self):
        super().__init__()
        # Entity(name="solid", position=(0,0), model=Mesh(vertices=[(0,0,0),(0.5,0.5,0),(0.5,1,0),(0,1,0)], triangles=[(0,1,2),(0,2,3)], mode='triangle', z=-1,  collider='box', visible=False))
        self.background = Entity(z=2, model='quad', texture=backgroundMap, scale= (30, 15), position=(0, 0))
        self.platformMap = Entity(z=1.5, model='quad', texture=platformMap, scale= (20, 12), position=(0, 0))
        
        self.ground1 = Entity(z=-1, name="solid", collider='box', model='quad', color= "#2a2f26", visible=False,scale=(4.65, 1.75), position=(-3.25, -3.15))
        self.ground2 = Entity(z=-1, name="solid", collider='box', model='quad', color= "#2a2f26", visible=False,scale=(4.3, 1.75), position=(4.45, -3.15))
        self.ground3 = Entity(z=-1, name="platform", collider='box', model='quad', color= "#636226", visible=False,scale=(3.24, 0.65), position=(0.69, -2.6))
        self.plat_left = Entity(z=-1, name="solid", collider='box', model='quad', color='#2f2629', visible=False, scale=(2.2, 3), position=(-6.4, 2.2))
        # self.plat_left = Entity(z=-1, name="solid", model=Mesh(vertices=[(-1.1, -2.5, 0),( 1.1, -0.5, 0),( 1.1,  2.5, 0),(-1.1,  2.5, 0)], triangles=[(0,1,2),(0,2,3)], mode='triangle'),  collider='mesh', visible=False, position=(-6.4, 1.2))
        self.plat_topr = Entity(z=-1, name="solid",collider='box', model='quad', color='#2f2629', visible=False, scale=(6.4, 1), position=(0, 1.7))
        self.plat_topm = Entity(z=-1, name="platform", collider='box', model='quad', color="#636226", visible=False, scale=(2.1, 0.65), position=(-4.25, 1.875))
        self.plat_right = Entity(z=-1, name="solid", collider='box', model='quad', color="#2f2629", visible=False, scale=(2.8, 1.15), position=(6.05, 3.9))
        invoke(self.init_characters, delay=0.5)
        camera.orthographic = True
        camera.fov = 10
        self.player = None
        self.enemy = None
        # self.plat_left.color = Color(0.39, 0.38, 0.15, 0.5)

    def init_characters(self):
        self.player = Kenzo(scale=(0.6, 0.75), position=(-2, 15))
        en = Kenzo(scale=(0.6, 0.75), position=(2, 15), type="enemy", facing="left")
        en.ai = AI(en, level = 1)
        self.enemy = [en]
        
        self.player.enemy = self.enemy
        for e in self.enemy:
            e.enemy = [self.player] +  [x for x in self.enemy if x is not e]
    
    def update(self):
        if self.player != None:
            if self.player.x > -5 and self.player.x < 5:
                camera.x = self.player.x
            if self.player.y > -2.5 and self.player.y <= 2.5:
                camera.y = self.player.y
            elif self.player.y > 2.5:
                camera.y = 2.5
            if self.player.y <= -20 or self.player.y >= 20 or self.player.x <= -5 and self.player.x >= 5:
                self.player.position=(0, 10)
                self.player.physics.velocity_y = 0
                self.player.velocity_y = 0
            for e in self.enemy:
                if e.ai != None:
                    e.ai.update()