# C'est ma partie UwU
from ursina import *
from game.core.variables import Variables
from game.core.utils import JumpSmoke
from game.core.attack import Attack

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
        self.velocity_x = 0
        self.jump_smoke = JumpSmoke(self.player)
        self.speed = Variables.PLAYER_SPEED
        self.is_attacking = False
        self.switch_facing = ""
        self.jump_side = 0
        self.attack_collider = None
        self.knockback = Vec3(0, 0, 0)
        self.ignore = player.enemy + player.team
        self.timer = 0
        self.kokoro_heal = 0
        self.isDashing = False
        self.surface_normal = Vec3(0, 0, 0)
        self.old_surface_normal = Vec3(0, 0, 0)
        self.isThrowing = False
        self.timerShuriken = 0
    
    def is_knockback(self, timing = 0.5, slowing = True):
        if self.knockback != Vec3(0, 0, 0):
            if self.surface_normal != Vec3(0, 0, 0) and self.old_surface_normal != self.surface_normal and not self.isDashing:
                self.old_surface_normal = self.surface_normal
                self.knockback = self.knockback - (2 * ((self.knockback[0] * self.surface_normal[0]) + (self.knockback[1] * self.surface_normal[1])) * self.surface_normal)
            
            self.player.inputManager.activate_input = False
            if self.timer < timing:
                self.velocity_x = self.knockback[0]
                if self.knockback[1] != 0:
                    self.velocity_y = self.knockback[1]
                elif slowing:
                    self.knockback[1] = 0.05 * (self.player.kokoro - 0.5)
                self.timer += time.dt
            elif not self.isDashing:
                self.player.inputManager.activate_input = True
                if abs(self.knockback[1]) <= 0.1:
                    self.knockback[1] = 0
                else:
                    if self.knockback[1] > 0:
                        self.knockback[1] -= (time.dt * self.gravity)
                    elif self.knockback[1] < -self.gravity:
                        self.knockback[1] += (time.dt * 10)
                    else:
                        self.knockback[1] = 0
                if self.knockback[1] != 0:
                    self.velocity_y = self.knockback[1]
                if abs(self.knockback[0]) <= 0.1:
                    self.knockback[0] = 0
                else:
                    if self.knockback[0] > 0:
                        self.knockback[0] -= (time.dt * 10)
                    elif self.knockback[0] < 0:
                        self.knockback[0] += (time.dt * 10)
                self.velocity_x = self.knockback[0]
            else:
                self.knockback = Vec3(0, 0, 0)
                self.velocity_x = self.knockback[0]      
        else:
            self.surface_normal = Vec3(0, 0, 0)
            self.timer = 0    
            self.old_surface_normal = Vec3(0, 0, 0)

    def throw_shuriken(self):
        player = self.player
        if "ThrowAttack" in player.animManager.animations:
            if player.inputManager.inputs["throw"] == 1:
                if not self.isThrowing and not self.is_attacking:
                    self.is_attacking = True
                    self.isThrowing = True
                    player.inputManager.activate_input = False
                    player.animManager.play("ThrowAttack", "play")
                    player.animManager.animations["ThrowAttack"][player.facing].input = "throw"
        if self.isThrowing:
            self.timerShuriken += time.dt
            if self.timerShuriken > 1.5:
                if self.attack_collider != None:
                    destroy(self.attack_collider)
                self.attack_collider = None
                self.isThrowing = False
                self.timerShuriken = 0

    def collision_x(self, move_x):
        player = self.player
        if self.velocity_x == 0:
            player.x += move_x
        else:
            player.x += self.velocity_x * time.dt
        hit_info = player.intersects(ignore=self.ignore)
        if hit_info.hit:
            for entity in hit_info.entities:
                self.slow_jump = 1
                if ((self.velocity_x == 0 and move_x > 0) or self.velocity_x > 0):
                    if entity.name == "solid":
                        left_entity = entity.x - entity.scale_x/2
                        player.x = left_entity - player.scale_val[0] * player.scale_x / 2 - 0.001
                    if entity.name != "attack_collider":
                        self.surface_normal = Vec3(-1, 0, 0)
                elif ((self.velocity_x == 0 and move_x <= 0) or self.velocity_x <= 0):
                    if entity.name == "solid":
                        right_entity = entity.x + entity.scale_x / 2
                        player.x = right_entity + player.scale_val[0] * player.scale_x/2 + 0.001
                    if entity.name != "attack_collider" :
                        self.surface_normal = Vec3(1, 0, 0)
                if self.velocity_y >= 0:
                    self.gravity = Variables.GRAVITY
            else:
                self.gravity = Variables.GRAVITY
        player.animManager.walk(player, hit_info)

    def collision_y(self, move_y):
        player = self.player
        player.y += move_y
        hit_info = player.intersects(ignore=self.ignore)
        if hit_info.hit:
            entity = hit_info.entity
            if entity.name != "solid":
                self.get_off()
            else :
                self.jump_right = False
                self.jump_left = False
                self.switch_facing = ""
                self.slow_jump = 1
            if move_y > 0:
                if entity.name != "attack_collider" :
                    self.surface_normal = Vec3(0, -1, 0)
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
                        self.dash()
                        if entity.name != "attack_collider":
                            self.surface_normal = Vec3(0, 1, 0)
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
                        if move_x > 0:
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
                    player.y -= self.gravity * time.dt
                    hit_info_y = player.intersects(ignore=self.ignore)
                    player.y = player_y
                    if hit_info_x.hit and hit_info_x.entity.name != "attack_collider" :
                        if i == 0 :
                            self.surface_normal = Vec3(-1, 0, 0)
                        else:
                            self.surface_normal = Vec3(0, 0, 0)
                    if hit_info_x.hit:
                        for entity in hit_info_x.entities:
                            if entity.name == "solid":
                                if not hit_info_y.hit or self.isGet_off:
                                    if not any(anim in player.animManager.animations and player.currentAnim == player.animManager.animations[anim][player.facing] for anim in ["JumpAttack", "MainAttack", "DashAttack", "AirAttack", "ThrowAttack", "WallSlide"]):
                                        if self.surface_normal[0] == -1:
                                            player.animManager.jump("WallSlide", "left")
                                        else:
                                            player.animManager.jump("WallSlide", "right")
                                else:
                                    player.animManager.play("Idle")
                            elif self.isGet_off :
                                if "JumpStart" in player.animManager.animations and int(self.velocity_y) == 0 :
                                    player.animManager.jump("JumpTransition")
                                elif "WallSlide" in player.animManager.animations and int(self.velocity_y) < Variables.GRAVITY and player.currentAnim != player.animManager.animations["WallSlide"][player.facing] :
                                    player.animManager.jump("JumpEnd")
        if self.velocity_y < 0 and (self.jump_left or self.jump_right):
            self.slow_jump -= self.slow_jump * time.dt * 2
            self.slow_jump = max(0.05, self.slow_jump)

    def dash(self):
        player = self.player
        if "Dash" in player.animManager.animations:
            if player.inputManager.inputs["dash"] == 1:
                if not self.isDashing:
                    player.inputManager.activate_input = False
                    player.animManager.play("Dash", "play")
                    if player.facing == "right":
                        self.knockback = Vec3(8, 0, 0)
                    else:
                        self.knockback = Vec3(-8, 0, 0)
                    player.animManager.animations["Dash"][player.facing].input = "dash"
                self.isDashing = True

    def update(self):
        player = self.player
        if not self.isDashing:
            self.is_knockback()
        else:
            self.is_knockback(0.5, False)
        if self.knockback[1] == 0:
            self.velocity_y -= self.gravity * time.dt
            if self.velocity_y < 0:
                self.velocity_y = max(self.velocity_y, -25)
        move_x = 0
        if player.inputManager.activate_input :
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
        self.jump()
        self.collision_x(move_x)
        if self.velocity_y > 0 and not self.mid_jump:
            h_max = (self.jump_force ** 2) / (2 * self.gravity) 
            half_jump_y = self.jump_start_y + h_max / 2
            if player.y >= half_jump_y:
                self.mid_jump = True
        self.collision_y(self.velocity_y * time.dt)
        self.throw_shuriken()
        if player.inputManager.inputs["dash"] == 0 and self.isDashing:
            self.isDashing = False
            player.inputManager.activate_input = True
        if self.is_attacking and self.attack_collider == None and not self.isGet_off:
            if player.facing == "right":
                if self.isThrowing:
                    self.attack_collider = Attack([0.35, 0.35], [player.x + player.scale_x / 4, player.y - player.scale_y / 6], player)
                else:
                    self.attack_collider = Attack([1.25, 1], [player.x + player.scale_x / 4, player.y - player.scale_y / 6], player)
            else:
                if self.isThrowing:
                    self.attack_collider = Attack([0.35, 0.35], [player.x - player.scale_x /4, player.y - player.scale_y/6], player)
                else:
                    self.attack_collider = Attack([1.25, 1], [player.x - player.scale_x /4, player.y - player.scale_y/6], player)
        if not self.is_attacking and not self.isThrowing:
            if self.attack_collider != None:
                destroy(self.attack_collider)
            self.attack_collider = None
        player.inputManager.update_inputs()