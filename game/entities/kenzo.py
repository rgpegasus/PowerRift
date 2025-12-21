from ursina import *
from game.manager.input import inputManager
from game.manager.resource import resourceManager
from game.manager.animation import AnimationManager
from game.core.physics import Physics

JumpEnd = resourceManager.picture("kenzo/jump/end/basic")

number_frames = {
    "Idle" : 10,
    "Walk" : 12,
    "Run" : 16,
    "Dash" : 16,
    "JumpStart" : 3,
    "JumpTransition" : 3,
    "JumpEnd" : 3,

    "WallJump" : 3,
    "WallClimbing" : 8,
    "WallContact" : 3,
    "WallSlide" : 3,

    "MainAttack" : 5,
    "ComboAttack" : 7,
    "JumpAttack" : 14,
    "AirAttack" : 6,
    "DashAttack" : 6,

    "Defend" : 6,
    "Healing" : 15,
    "Hurt" : 4,
    "Death" : 9
}


class Kenzo(Entity):
    def __init__(self,**kwargs):
        super().__init__(
            model="quad", 
            name="player",
            texture= JumpEnd,
            **kwargs
        )
        self.scale_val = (0.15,0.33)
        self.scale=3.5
        self.collider = BoxCollider(self, size=Vec3(self.scale_val[0], self.scale_val[1], 1), center=(0, -0.178, 0))
        self.speed_variation = 1

        self.playername = "kenzo"
        self.facing = "right"
        self.animManager = AnimationManager(self, self.playername, number_frames)
        self.physics = Physics(self)
        self.currentAnim = self.animManager.animations["JumpEnd"]["right"]
        self.currentAnim.loop()

    def update(self):
        self.physics.update()
        self.animManager.update() 


