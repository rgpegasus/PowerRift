from game.manager.resource import resourceManager
from game.core.utils import Animation
from game.manager.input import inputManager
import time 
class AnimationManager:
    def __init__(self, player, name, number_frames):
        self.animations = {
            "Idle" : f"{name}/idle/basic",
            "Walk" : f"{name}/walk/basic",
            "Run" : f"{name}/run/basic",
            "Dash" : f"{name}/dash/basic",
            "JumpStart" : f"{name}/jump/start/basic",
            "JumpTransition" :f"{name}/jump/transition/basic",
            "JumpEnd" : f"{name}/jump/end/basic",
            "WallJump" : f"{name}/wall/jump/basic",
            "WallClimbing" : f"{name}/wall/contact/basic",
            "WallSlide" : f"{name}/wall/slide/basic",
            "MainAttack" : f"{name}/attacks/main/basic",
            "ComboAttack" : f"{name}/attacks/combo/basic",
            "JumpAttack" : f"{name}/attacks/jump/basic",
            "AirAttack" : f"{name}/attacks/air/basic",
            "DashAttack" : f"{name}/attacks/dash/basic",
            "Defend" : f"{name}/defend/basic",
            "Healing" : f"{name}/healing/basic",
            "Hurt" : f"{name}/hurt/basic",
            "Death" : f"{name}/death/basic",
        }
        
        wrong = []
        for anim, path in self.animations.items():
            if anim in number_frames:
                full_path = resourceManager.picture(path)
                nbf = number_frames[anim]
                self.animations[anim] = {
                    "right" : Animation(player, full_path, nbf),
                    "left" : Animation(player, full_path, nbf, direction=-1),
                    "frames" : nbf,
                }
            else:
                wrong.append(anim)
        for anim in wrong:
            self.animations.pop(anim, None)
        self.player = player

        

    def play(self, name, type = "loop", new_facing = ""):
        if name in self.animations:
            player = self.player
            anim = self.animations[name][player.facing]
            if player.currentAnim != anim:
                player.currentAnim = anim
                if new_facing!= "":
                    player.facing = new_facing

                player.texture_offset = (0 / self.animations[name]["frames"], 0)
                if type == "loop":
                    player.currentAnim.loop()
                else:
                    player.currentAnim.play()

    def jump(self, step, new_facing = ""):
        player = self.player
        if player.currentAnim != self.animations["AirAttack"][player.facing] or player.currentAnim.end:
            if step == "JumpTransition" or step == "WallJump" or step == "WallClimbing":
                self.play(step, "play", new_facing)
            elif step == "JumpStart" or step == "JumpEnd" or step == "WallSlide":
                self.play(step, "loop", new_facing)
    
    def walk(self, player):
        directions = ["left", "right"]
        player_x = player.x
        move_x = 0
        if player.facing == "right":
            move_x += player.physics.speed * player.speed_variation * time.dt
        elif player.facing == "left":
            move_x -= player.physics.speed * player.speed_variation * time.dt
        player.x += move_x
        hit_info = player.intersects()
        player.x = player_x
        if not hit_info.hit:
            for direction in directions:
                if inputManager.pressed(direction) :
                    if any(anim in self.animations and player.currentAnim == self.animations[anim][direction] for anim in ["JumpStart", "JumpTransition", "JumpEnd"]):
                        player.facing = direction
                        return
                    elif player.physics.can_move and not player.physics.is_attacking and not player.physics.crossing and not player.physics.isGet_off :
                        player.facing = direction
                        self.play("Run", "loop")
                        # if inputManager.pressed("dash"):
                        #     self.play("Run", "loop")
                        #     player.speed_variation = 1
                        # else:
                        #     self.play("Walk", "loop")
                        #     player.speed_variation = 0.5
            else:   
                if ((any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["Idle", "Walk", "Run", "WallSlide"]) and inputManager.no_input()) or player.currentAnim.end) and int(player.physics.velocity_y) == 0 :
                    self.play("Idle", "loop")
                

    def attack(self, player):
        if not any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["JumpAttack", "MainAttack", "DashAttack", "AirAttack", "Defend"]) and (player.physics.is_attacking or not player.physics.can_move):
            player.physics.is_attacking = False
            player.physics.can_move = True
        if not player.physics.is_attacking and not player.physics.isGet_off:
            inputAttack = inputManager.click("attack")
            if not any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["JumpStart", "JumpTransition", "JumpEnd"]):
                if inputManager.combo_pressed(["up", "attack"]) :
                    self.play("JumpAttack", "play")
                    player.physics.is_attacking = True
                    player.physics.can_move = False
                elif inputManager.combo_pressed(["dash", "attack"]) :
                    self.play("DashAttack", "play")
                    player.physics.is_attacking = True
                    player.physics.can_move = False
                elif inputAttack:
                    self.play("MainAttack", "play")
                    player.physics.is_attacking = True
                    player.physics.can_move = False
            elif inputAttack :
                self.play("AirAttack", "play")
                player.physics.is_attacking = True
        if inputManager.click("defend") and not player.physics.is_attacking and not any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["JumpStart", "JumpTransition", "JumpEnd"]) and not player.physics.isGet_off:
            self.play("Defend", "play")
            player.physics.can_move = False
            


    def update(self):
        player = self.player
        self.attack(player)
        self.walk(player)
        if player.physics.switch_facing != player.facing and player.physics.switch_facing:
            player.facing = player.physics.switch_facing
        if inputManager.click("interact"):
            self.play("Healing", "play")
            player.physics.can_move = False
        player.currentAnim.update()
        
    
    


