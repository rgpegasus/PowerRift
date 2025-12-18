from ursina import *
from game.manager.input import inputManager
from game.manager.resource import resourceManager
from game.core.physics import Physics
from game.core.utils import Animation 
import random


Idle = resourceManager.picture("demon/idle/right")
Walk = resourceManager.picture("demon/walk/right")
MainAttack = resourceManager.picture("demon/attacks/main/right")
ComboAttack = resourceManager.picture("demon/attacks/combo/right")
DownAttack = resourceManager.picture("demon/attacks/down/right")
JumpAttack = resourceManager.picture("demon/attacks/jump/right")
Defend = resourceManager.picture("demon/defend/right")
Shout = resourceManager.picture("demon/shout/right")


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

        self.animIdleRight = Animation(self, Idle, 6)
        self.animWalkRight = Animation(self, Walk, 8)
        self.animMainAttackRight = Animation(self, MainAttack, 7)
        self.animComboAttackRight = Animation(self, ComboAttack, 5)
        self.animDownAttackRight = Animation(self, DownAttack, 5)
        self.animJumpAttackRight = Animation(self, JumpAttack, 12)
        self.animDefendRight = Animation(self, Defend, 6)
        self.animShoutRight = Animation(self, Shout, 17)

        self.animIdleLeft = Animation(self, Idle, 6, direction = -1)
        self.animWalkLeft = Animation(self, Walk, 8, direction = -1)
        self.animMainAttackLeft = Animation(self, MainAttack, 7, direction = -1)
        self.animComboAttackLeft = Animation(self, ComboAttack, 5, direction = -1)
        self.animDownAttackLeft = Animation(self, DownAttack, 5, direction = -1)
        self.animJumpAttackLeft = Animation(self, JumpAttack, 12, direction = -1)
        self.animDefendLeft = Animation(self, Defend, 6, direction = -1)
        self.animShouLeft = Animation(self, Shout, 17, direction = -1)

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
        self.y -=0.001
        hit_info = self.intersects()
        self.y +=0.001
        if hit_info.hit and self.physics.is_attacking and self.currentAnim.end :
            self.physics.is_attacking = False
            self.physics.can_move = True
        if inputManager.click("play"):
            if self.currentAnim != self.animShoutRight and self.was_right:
                self.currentAnim = self.animShoutRight
                self.texture_offset = (0 / 17, 0)
                self.currentAnim.play()
            elif self.currentAnim != self.animShouLeft and self.was_left:
                self.currentAnim = self.animShouLeft
                self.texture_offset = (0 / 17, 0)
                self.currentAnim.play()
            self.physics.is_attacking = True
            self.physics.can_move = False
        if (self.physics.velocity_y > 0.3 or self.physics.velocity_y < -0.3 ) and not self.physics.is_attacking and inputManager.click("attack"):
            if self.currentAnim != self.animDownAttackLeft and self.was_left:
                self.currentAnim = self.animDownAttackLeft
                self.texture_offset = (0 / 5, 0)
                self.currentAnim.play()
            elif self.currentAnim != self.animDownAttackRight and self.was_right:
                self.currentAnim = self.animJumpAttackRight
                self.texture_offset = (0 / 5, 0)
                self.currentAnim.play()
            self.physics.is_attacking = True
            self.physics.can_move = False

        elif inputManager.combo_pressed(["up", "attack"]) and not self.physics.is_attacking:
            if self.currentAnim != self.animJumpAttackLeft and self.was_left:
                self.currentAnim = self.animJumpAttackLeft
                self.texture_offset = (0 / 7, 0)
                self.currentAnim.play()
            elif self.currentAnim != self.animJumpAttackRight and self.was_right:
                self.currentAnim = self.animJumpAttackRight
                self.texture_offset = (0 / 7, 0)
                self.currentAnim.play()
            self.physics.is_attacking = True
            self.physics.can_move = False
        
        elif inputManager.click("attack") and int(self.physics.velocity_y) == 0 and not self.physics.is_attacking :
            animRight = random.choice([self.animMainAttackRight, self.animComboAttackRight])
            animLeft = random.choice([self.animMainAttackLeft, self.animComboAttackLeft])
            if self.currentAnim != animLeft and self.was_left:
                self.currentAnim = animLeft
                if animLeft == self.animMainAttackLeft:
                    self.texture_offset = (0 / 7, 0)
                else:
                    self.texture_offset = (0 / 5, 0)
                self.currentAnim.play()
            elif self.currentAnim != animRight and self.was_right:
                self.currentAnim = animRight
                if animRight == self.animMainAttackRight:
                    self.texture_offset = (0 / 7, 0)
                else:
                    self.texture_offset = (0 / 5, 0)
                self.currentAnim.play()
            self.physics.is_attacking = True
            self.physics.can_move = False

        if (self.physics.can_move and not self.physics.is_attacking) and (self.currentAnim not in (self.animJumpAttackLeft, self.animJumpAttackRight) or self.currentAnim.end):
            if inputManager.click("defend"):
                if self.currentAnim != self.animDefendLeft and self.was_left:
                    self.currentAnim = self.animDefendLeft
                    self.texture_offset = (0 / 6, 0)
                    self.currentAnim.play()
                elif self.currentAnim != self.animDefendRight and self.was_right:
                    self.currentAnim = self.animDefendRight
                    self.texture_offset = (0 / 6, 0)
                    self.currentAnim.play()
                self.physics.is_attacking = True
                self.physics.can_move = False
            elif (inputManager.pressed("left") and (not self.physics.switch_right)) or self.physics.switch_left:
                moving = True
                if self.currentAnim != self.animWalkLeft :
                    self.currentAnim = self.animWalkLeft
                    self.was_right = False
                    self.was_left = True
                    self.texture_offset = (0 / 8, 0)
                    self.currentAnim.loop()
            elif (inputManager.pressed("right") and (not self.physics.switch_left)) or self.physics.switch_right:
                moving = True
                if self.currentAnim != self.animWalkRight:
                    self.currentAnim = self.animWalkRight
                    self.was_right = True
                    self.was_left = False
                    self.texture_offset = (0 / 8, 0)
                    self.currentAnim.loop()
            elif not moving and self.was_right and not self.was_left:
                if self.currentAnim != self.animIdleRight:
                    self.currentAnim = self.animIdleRight
                    self.texture_offset = (0 / 6, 0)
                    self.currentAnim.loop()
            elif not moving and not self.was_right and self.was_left:
                if self.currentAnim != self.animIdleLeft:
                    self.currentAnim = self.animIdleLeft
                    self.texture_offset = (0 / 6, 0)
                    self.currentAnim.loop()
