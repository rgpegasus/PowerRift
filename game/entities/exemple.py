from ursina import *
from game.manager.input import inputManager
from game.manager.resource import resourceManager
from game.core.physics import Physics
from game.core.utils import Animation 



knightIdleRight = resourceManager.picture("knight/idle/right")
knightWalkRight = resourceManager.picture("knight/walk/right")
knightAttackRight = resourceManager.picture("knight/attack/right")
knightIdleLeft = resourceManager.picture("knight/idle/left")
knightWalkLeft = resourceManager.picture("knight/walk/left")
knightAttackLeft = resourceManager.picture("knight/attack/left")  

class Exemple(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model="quad", 
            texture= knightIdleRight,
            **kwargs
        )
        
        self.scale_val = (0.0825, 0.11)
        self.scale=7
        self.collider = BoxCollider(self, size=Vec3(self.scale_val[0], self.scale_val[1], 1))
        self.speed_variation = 1

        self.animIdleRight = Animation(self, knightIdleRight, 5)
        self.animWalkRight = Animation(self, knightWalkRight, 4)
        self.animAttackRight = Animation(self, knightAttackRight, 8)

        self.animIdleLeft = Animation(self, knightIdleLeft, 5)
        self.animWalkLeft = Animation(self, knightWalkLeft, 4)
        self.animAttackLeft = Animation(self, knightAttackLeft, 8)
        
        self.currentAnim = self.animIdleRight
        self.currentAnim.loop()
        self.was_right = True
        self.was_left = False
        self.physics = Physics(self)

    def update(self):
        self.move()
        self.physics.update()
        self.currentAnim.update() 

    def move(self):
        moving = False
        if (self.currentAnim == self.animAttackLeft or self.animAttackRight) and self.currentAnim.end:
            self.physics.is_attacking = False
        if inputManager.click("attack") and int(self.physics.velocity_y) == 0 :
            if self.currentAnim != self.animAttackLeft and self.was_left:
                self.physics.is_attacking = True
                self.currentAnim = self.animAttackLeft
                self.texture_offset = (0 / 8, 0)
                self.currentAnim.play()
            elif self.currentAnim != self.animAttackRight and self.was_right:
                self.physics.is_attacking = True
                self.currentAnim = self.animAttackRight
                self.texture_offset = (0 / 8, 0)
                self.currentAnim.play()
        if not self.physics.is_attacking:
            if (inputManager.pressed("left") and ( not self.physics.switch_right)) or self.physics.switch_left:
                moving = True
                if self.currentAnim != self.animWalkLeft:
                    self.currentAnim = self.animWalkLeft
                    self.was_right = False
                    self.was_left = True
                    self.texture_offset = (0 / 4, 0)
                    self.currentAnim.loop()
            elif (inputManager.pressed("right") and ( not self.physics.switch_left)) or self.physics.switch_right:
                moving = True
                if self.currentAnim != self.animWalkRight:
                    self.currentAnim = self.animWalkRight
                    self.was_right = True
                    self.was_left = False
                    self.texture_offset = (0 / 4, 0)
                    self.currentAnim.loop()
            elif not moving and self.was_right and not self.was_left:
                if self.currentAnim != self.animIdleRight:
                    self.currentAnim = self.animIdleRight
                    self.texture_offset = (0 / 5, 0)
                    self.currentAnim.loop()
            elif not moving and not self.was_right and self.was_left:
                if self.currentAnim != self.animIdleLeft:
                    self.currentAnim = self.animIdleLeft
                    self.texture_offset = (0 / 5, 0)
                    self.currentAnim.loop()
