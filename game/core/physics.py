# C'est ma partie UwU
from ursina import *
from game.core.variables import Variables
from game.core.utils import JumpSmoke
from game.core.attack import Attack
class Physics:
    def __init__(self, player):
        self.player = player
        self.player
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
        self.speed = Variables.PLAYER_SPEED
        self.is_attacking = False
        self.switch_facing = ""
        self.jump_side = 0
        self.can_move = True
        self.attack_collider = None
        self.ignore = player.enemy + player.team
        
    def collision_x(self, move_x):
        player = self.player
        player.x += move_x
        hit_info = player.intersects(ignore=self.ignore)
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
        hit_info = player.intersects(ignore=self.ignore)
        if hit_info.hit :
            entity = hit_info.entity
            if entity.name != "solid":
                self.get_off()
                if self.isGet_off:
                    player.animManager.jump("JumpTransition")
            
            self.jump_right = False
            self.jump_left = False
            self.switch_facing = ""
            self.slow_jump = 1
            if move_y > 0 :
                if entity.name == "solid":   
                    bottom_entity = entity.y - entity.scale_y/2
                    player.y = bottom_entity - player.scale_val[1] * player.scale_y/2 - 0.001 - player.collider.center[1] * player.scale_y
                    self.velocity_y = 0
                else:  
                    self.crossing = True
            else: 
                entities = hit_info.entities
                for entity in entities:
                    if entity.name == 'solid' or not self.isGet_off and not self.crossing:
                        top_entity = entity.y + entity.scale_y/2
                        player.y = top_entity + player.scale_val[1] * player.scale_y/2 + 0.001 - player.collider.center[1] * player.scale_y
                        self.velocity_y = 0
                        self.remaining_jump = Variables.MAX_JUMP
                        self.jump_side = 0
            if any(anim in player.animManager.animations and player.currentAnim == player.animManager.animations[anim][player.facing] for anim in ["JumpStart", "JumpTransition", "JumpEnd"]) and ((not self.isGet_off and not self.crossing) or entity.name == "solid"):
                player.animManager.play("Idle", "loop")
        else:
            if "JumpStart" in player.animManager.animations and int(self.velocity_y) == 0 and player.currentAnim == player.animManager.animations["JumpStart"][player.facing] :
                player.animManager.jump("JumpTransition")
            elif "WallSlide" in player.animManager.animations and int(self.velocity_y) < 0 and player.currentAnim != player.animManager.animations["WallSlide"][player.facing] :
                player.animManager.jump("JumpEnd")
            if self.crossing :
                self.crossing = False
            self.isGet_off = False
            

    def get_off(self):
        player = self.player
        if player.inputManager.inputs["get off"] == 2:
            self.isGet_off = True
            
    def jump(self):
        player = self.player
        player_x = player.x
        player_y = player.y
        if player.inputManager.inputs["jump"] == 1:
            self.jump_side += 1
            compte = 0
            for i in range(2):
                move_x = 0
                if i == 0:
                    move_x -= self.speed * self.player.speed_variation * time.dt
                else:
                    move_x += self.speed * self.player.speed_variation * time.dt
                player.x += move_x
                hit_info = player.intersects(ignore=self.ignore)
                player.x = player_x
                if hit_info.hit :
                    entity = hit_info.entity
                    if entity.name == "solid":
                        if move_x>0:
                            self.jump_smoke.isJumping("left", self.jump_side >= 9)
                            self.jump_left = True
                            self.jump_right = False
                            self.switch_facing = "left"
                        elif move_x < 0:
                            self.jump_smoke.isJumping("right", self.jump_side >= 9)
                            self.jump_right = True
                            self.jump_left = False
                            self.switch_facing = "right"
                        player.animManager.jump("WallJump")
                    self.remaining_jump = max(1,min(10 - self.jump_side, Variables.MAX_JUMP))
                elif self.jump_left or self.jump_right :
                    if 10 - self.jump_side < Variables.MAX_JUMP:
                        self.remaining_jump = max(0, 10 - self.jump_side)
                if not hit_info:
                    compte+=1
            if compte == 2:
                player.animManager.jump("JumpStart")
            if self.remaining_jump > 0 :
                if not self.jump_left and not self.jump_right:
                    self.jump_smoke.isJumping("down")
                self.velocity_y = self.jump_force
                self.remaining_jump -= 1
                self.jump_start_y = player.y
                self.mid_jump = False
        else:   
            if self.velocity_y < 0:    
                for i in range(2):
                    move_x = 0
                    if i == 0:
                        move_x -= self.speed * self.player.speed_variation * time.dt
                    else:
                        move_x += self.speed * self.player.speed_variation * time.dt
                    player.x += move_x
                    hit_info_x = player.intersects(ignore=self.ignore)
                    player.x = player_x
                    player.y += self.velocity_y
                    hit_info_y = player.intersects(ignore=self.ignore)
                    player.y = player_y
                    if hit_info_x.hit and hit_info_x.entity.name == "solid":
                        if not hit_info_y.hit :
                            if "WallSlide" in player.animManager.animations and not any(anim in player.animManager.animations and player.currentAnim == player.animManager.animations[anim][player.facing] for anim in ["JumpAttack", "MainAttack", "DashAttack", "AirAttack", "WallSlide"]):
                                player.animManager.jump("WallSlide")
                        else:
                            player.animManager.play("Idle")
        if self.velocity_y < 0 and (self.jump_left or self.jump_right):
            self.slow_jump -= self.slow_jump * time.dt * 2
            self.slow_jump = max(0.05, self.slow_jump)

    def update(self):
        player = self.player
        self.velocity_y -= self.gravity * time.dt
        if self.velocity_y < 0:
            self.velocity_y = max(self.velocity_y, -25)
        move_x = 0
        if self.can_move :
            if player.inputManager.inputs["left"] == 2 and (self.mid_jump or not self.jump_right) or self.jump_left :
                if player.inputManager.inputs["left"] == 2 and self.mid_jump:
                    self.jump_left = False
                    self.jump_right = False
                    self.switch_facing = ""
                move_x -= self.speed * self.player.speed_variation * time.dt * self.slow_jump
            if player.inputManager.inputs["right"] == 2 and (self.mid_jump or not self.jump_left) or self.jump_right :
                if  player.inputManager.inputs["right"] == 2 and self.mid_jump:
                    self.jump_right = False
                    self.jump_left = False
                    self.switch_facing = ""
                move_x += self.speed * self.player.speed_variation * time.dt * self.slow_jump
        self.collision_x(move_x)
        if self.velocity_y > 0 and not self.mid_jump:
            h_max = (self.jump_force ** 2) / (2 * self.gravity) 
            half_jump_y = self.jump_start_y + h_max / 2
            if player.y >= half_jump_y:
                self.mid_jump = True
        self.collision_y(self.velocity_y * time.dt)
        self.jump()
        
        if self.is_attacking and self.attack_collider == None:
            if player.facing == "right":
                self.attack_collider = Attack([1, 1], [player.x + player.scale_x / 4, player.y - player.scale_y / 6], player)
            else:
                self.attack_collider = Attack([1, 1], [player.x - player.scale_x /4, player.y - player.scale_y/6], player)
        if not self.is_attacking:
            if self.attack_collider != None:
                destroy(self.attack_collider)
            self.attack_collider = None
        player.inputManager.update_inputs()
        
