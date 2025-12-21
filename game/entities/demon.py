from ursina import *
from game.manager.input import inputManager
from game.manager.resource import resourceManager
from game.core.physics import Physics
from game.manager.animation import AnimationManager


Idle = resourceManager.picture("demon/idle/basic")
number_frames = {
    "Idle" : 6,
    "Run" : 8,

    "MainAttack" : 7,
    "ComboAttack" : 5,
    "JumpAttack" : 12,
    "AirAttack" : 5,

    "Defend" : 6,
    "Hurt" : 4,
    "Death" : 26
}


class Demon(Entity):
    def __init__(self,**kwargs):
        super().__init__(
            model="quad", 
            name="player",
            texture= Idle,
            **kwargs
        )
        
        self.scale_val = (0.18,0.475)
        self.scale=2.5
        self.collider = BoxCollider(self, size=Vec3(self.scale_val[0], self.scale_val[1], 1), center=(0, -0.15, 0))

        self.speed_variation = 1

        self.playername = "demon"
        self.facing = "right"
        self.animManager = AnimationManager(self, self.playername, number_frames)
        self.physics = Physics(self)
        self.currentAnim = self.animManager.animations["Idle"]["right"]
        self.currentAnim.loop()
        

    def update(self):
        self.physics.update()
        self.animManager.update() 
