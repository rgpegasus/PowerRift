from game.manager.resource import resourceManager
from game.core.utils import Animation
import time
from ursina import Vec3, Audio

_sounds = {}

def _play(name):
    if name not in _sounds:
        try:
            _sounds[name] = Audio(f'game/resources/sounds/music/{name}', autoplay=False, loop=False)
        except Exception:
            _sounds[name] = None
    s = _sounds.get(name)
    if s:
        try:
            s.play()
        except Exception:
            pass

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
            "DashAttack": f"{name}/attacks/dash/basic",
            "ThrowAttack": f"{name}/attacks/throw/basic",
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
                    "frames": nbf,
                }
            else:
                wrong.append(anim)
        for anim in wrong:
            self.animations.pop(anim, None)
        self.player = player

    def play(self, name, type="loop", new_facing=""):
        player = self.player
        if name in self.animations :
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
        if (player.currentAnim != self.animations["AirAttack"][player.facing] and not player.physics.is_attacking) or player.currentAnim.end:
            if step == "JumpTransition" or step == "WallJump" or step == "WallClimbing":
                self.play(step, "play", new_facing)
            elif step == "JumpStart" or step == "JumpEnd" or step == "WallSlide":
                self.play(step, "loop", new_facing)
    
    def walk(self, player, hit_info):
        if not hit_info.hit and player.currentAnim != self.animations["Death"][player.facing]:
            for direction in ["left", "right"]:
                if player.inputManager.inputs[direction] == 2 :
                    if any(anim in self.animations and player.currentAnim == self.animations[anim][direction] for anim in ["JumpStart", "JumpTransition", "JumpEnd"]):
                        player.facing = direction
                        return
                    elif player.inputManager.activate_input and not player.physics.is_attacking and not player.physics.crossing and not player.physics.isGet_off and player.inputManager.inputs["jump"] == 0:
                        player.facing = direction
                        self.play("Run", "loop")
            else:
                if ((any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["Idle", "Walk", "Run", "WallSlide", "Death"]) and player.inputManager.no_input()) or player.currentAnim.end) and int(player.physics.velocity_y) == 0 :
                    self.play("Idle", "loop")
        elif (not (any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["Idle", "WallSlide", "Death", "Hurt", "Healing", "Defend"]) and not player.physics.is_attacking) or player.currentAnim.end) and int(player.physics.velocity_y) == 0 :
                self.play("Idle", "loop")


    def attack(self, player):
        if not any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["JumpAttack", "MainAttack", "DashAttack", "AirAttack", "ThrowAttack", "Defend"]) and (player.physics.is_attacking or not player.inputManager.activate_input):
            player.physics.is_attacking = False
            player.inputManager.activate_input = True
            player.inputManager.inputs["attack"] = 0
            player.inputManager.inputs["defend"] = 0
            player.inputManager.inputs["throw"] = 0
        if player.inputManager.activate_input:
            if not player.physics.is_attacking and not player.physics.isGet_off :
                inputAttack = player.inputManager.inputs["attack"] == 1
                if not any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["JumpStart", "JumpTransition", "JumpEnd", "WallSlide"]):
                    if player.inputManager.combo_pressed(["up", "attack"]) :
                        self.play("JumpAttack", "play")
                        player.physics.is_attacking = True
                        player.inputManager.activate_input = False
                        _play('slashup.wav')
                    elif player.inputManager.combo_pressed(["dash", "attack"]) :
                        self.play("DashAttack", "play")
                        player.physics.is_attacking = True
                        if player.facing == "right":
                            player.physics.knockback = Vec3(8, 0, 0)
                        else:
                            player.physics.knockback = Vec3(-8, 0, 0)
                        player.inputManager.activate_input = False
                        _play('slash.wav')
                    elif inputAttack:
                        self.play("MainAttack", "play")
                        player.physics.is_attacking = True
                        player.inputManager.activate_input = False
                        _play('slash.wav')
                elif inputAttack :
                    self.play("AirAttack", "play")
                    player.physics.is_attacking = True
                    _play('slash.wav')
            if player.inputManager.inputs["defend"] == 1 and not player.physics.is_attacking and not any(anim in self.animations and player.currentAnim == self.animations[anim][player.facing] for anim in ["JumpStart", "JumpTransition", "JumpEnd"]) and not player.physics.isGet_off :
                self.play("Defend", "play")
                player.inputManager.activate_input = False

    def update(self):
        player = self.player
        self.attack(player)
        if player.physics.switch_facing != player.facing and player.physics.switch_facing:
            player.facing = player.physics.switch_facing
        if player.kokoro > 1 and player.inputManager.activate_input:
            if player.inputManager.inputs["interact"] == 1 and "Healing" in self.animations and player.kokoro_steal > 0 and min(player.physics.kokoro_heal, 1) != 1:
                self.play("Healing", "play")
                player.inputManager.activate_input = False
                player.physics.kokoro_heal += 0.1
                player.kokoro_steal -= 0.1
            elif player.currentAnim == self.animations["Healing"][player.facing] and player.currentAnim.end:
                player.kokoro = max(player.kokoro - player.physics.kokoro_heal, 1)
        player.currentAnim.update()
