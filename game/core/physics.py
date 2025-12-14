# C'est ma partie UwU
from ursina import *
from game.core.variables import Variables
from game.manager.input import inputManager
from game.core.utils import JumpSmoke 
class Physics:
    def __init__(self, player):
        self.player = player
        self.gravity = Variables.GRAVITY
        self.jump_force = Variables.JUMP_FORCE
        self.isGet_off = False
        self.crossing = False
        self.jump_right = False
        self.jump_left = False
        self.jump_start_y = 0
        self.mid_jump = False
        self.slow_jump = 1
        self.remaining_jump = Variables.MAX_JUMP
        self.velocity_y = 0
        self.jump_smoke = JumpSmoke(self.player)
        self.speed = Variables.PLAYER_SPEED * self.player.speed_variation
        self.is_attacking = False
        self.switch_right = False
        self.switch_left = False
        self.jump_side = 0
        
    def collision_x(self, move_x):
        player = self.player
        player.x += move_x
        hit_info = player.intersects()
        if hit_info.hit:
            entity = hit_info.entity
            self.slow_jump = 1
            if move_x > 0 and entity.name == "solid":  
                left_entity = entity.x - entity.scale_x/2
                player.x = left_entity - player.scale_val[0] * player.scale_x/2 - 0.001
            elif move_x <= 0 and entity.name == "solid":
                right_entity = entity.x + entity.scale_x/2
                player.x = right_entity + player.scale_val[0] * player.scale_x/2 + 0.001
            if self.velocity_y < 0 and not self.isGet_off and not self.crossing or entity.name == 'solid':
                self.gravity = 3
            if self.velocity_y >= 0:
                self.gravity = Variables.GRAVITY
        else:
            self.gravity = Variables.GRAVITY

    def collision_y(self, move_y):
        player = self.player
        player.y += move_y
        hit_info = player.intersects()
        if hit_info.hit :
            entity = hit_info.entity
            self.jump_right = False
            self.jump_left = False
            self.switch_left = False
            self.switch_right = False
            self.slow_jump = 1
            if move_y > 0 :
                if entity.name == "solid":   
                    bottom_entity = entity.y - entity.scale_y/2
                    player.y = bottom_entity - player.scale_val[1] * player.scale_y/2 - 0.001
                    self.velocity_y = 0
                else:  
                    self.crossing = True
            else: 
                entities = hit_info.entities
                for entity in entities:
                    if entity.name == 'solid' or not self.isGet_off and not self.crossing:
                        top_entity = entity.y + entity.scale_y/2
                        player.y = top_entity + player.scale_val[1] * player.scale_y/2 + 0.001
                        self.velocity_y = 0
                        self.remaining_jump = Variables.MAX_JUMP
                        self.jump_side = 0
        else:
            if move_y > 0 and self.crossing :
                self.crossing=False
            self.isGet_off = False
            

    def get_off(self):
        if inputManager.pressed("get off") :
            self.isGet_off = True
            
    def jump(self):
        player = self.player
        player_x = player.x
        if inputManager.click("jump"):
            self.jump_side += 1
            for i in range(2):
                move_x = 0
                if i == 0:
                    move_x -= self.speed * time.dt
                else:
                    move_x += self.speed * time.dt
                player.x += move_x
                hit_info = player.intersects()
                player.x = player_x
                if hit_info.hit :
                    entity = hit_info.entity
                    if entity.name == "solid":
                        if move_x>0:
                            self.jump_smoke.isJumping("left", self.jump_side >= 9)
                            self.jump_left = True
                            self.jump_right = False
                            self.switch_left = True
                            self.switch_right = False
                        elif move_x < 0:
                            self.jump_smoke.isJumping("right", self.jump_side >= 9)
                            self.jump_right = True
                            self.jump_left = False
                            self.switch_right = True
                            self.switch_left = False

                    self.remaining_jump = max(1,min(10 - self.jump_side, Variables.MAX_JUMP))
                elif self.jump_left or self.jump_right :
                    if 10 - self.jump_side < Variables.MAX_JUMP:
                        self.remaining_jump = max(0, 10 - self.jump_side)
            if self.remaining_jump > 0 :
                if not self.jump_left and not self.jump_right:
                    self.jump_smoke.isJumping("down")
                self.velocity_y = self.jump_force
                self.remaining_jump -= 1
                self.jump_start_y = player.y
                self.mid_jump = False
                

        if self.velocity_y < 0 and (self.jump_left or self.jump_right):
            self.slow_jump -= self.slow_jump * time.dt * 2
            self.slow_jump = max(0.05, self.slow_jump)




    def update(self):
        player = self.player
        self.velocity_y -= self.gravity * time.dt
        if self.velocity_y < 0:
            self.velocity_y = max(self.velocity_y, -25)
        move_x = 0
        if not self.is_attacking :
            if inputManager.pressed("left") and (self.mid_jump or not self.jump_right) or self.jump_left :
                if inputManager.pressed("left") and self.mid_jump:
                    self.jump_left = False
                    self.jump_right = False
                    self.switch_right = False
                move_x -= self.speed * time.dt * self.slow_jump
            if inputManager.pressed("right") and (self.mid_jump or not self.jump_left) or self.jump_right :
                if inputManager.pressed("right") and self.mid_jump:
                    self.jump_right = False
                    self.jump_left = False
                    self.switch_left = False
                move_x += self.speed * time.dt * self.slow_jump
        self.get_off()
        self.collision_x(move_x)
        if self.velocity_y > 0 and not self.mid_jump:
            h_max = (self.jump_force ** 2) / (2 * self.gravity) 
            half_jump_y = self.jump_start_y + h_max / 2
            if player.y >= half_jump_y:
                self.mid_jump = True
        self.collision_y(self.velocity_y * time.dt)
        self.jump()
        
