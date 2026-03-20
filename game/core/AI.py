from ursina import *
from game.manager.input import InputManager
import random

class AI:
    def __init__(self, player, level=1):
        self.type = "AI"
        self.player = player
        self.level = level
        self.target = None
        self.inputs = {
            "left": 0, "right": 0, "up": 0, "dash": 0, 
            "get off": 0, "interact": 0, "defend": 0, 
            "jump": 0, "attack": 0, "play": 0
        }
        self.old_inputs = self.inputs.copy()
        self.data = {}
        self.timer = 0
        self.delay = 0.5 if level == 1 else 0.15

    def perceive(self):
        self.data["safe"] = self.player.physics.velocity_y == 0
        self.data["vel_y"] = self.player.physics.velocity_y
        
        pos = self.player.position
        self.data["void_c"] = not raycast(pos, Vec3(0, -1, 0), 5, ignore=([self.player] + self.player.team + self.player.enemy)).hit
        self.data["void_l"] = not raycast(pos + Vec3(-0.8, -0.5, 0), Vec3(0, -1, 0), 3, ignore=([self.player] + self.player.team + self.player.enemy)).hit
        self.data["void_r"] = not raycast(pos + Vec3(0.8, -0.5, 0), Vec3(0, -1, 0), 3, ignore=([self.player] + self.player.team + self.player.enemy)).hit

        if self.target == None:
            for e in scene.entities:
                if getattr(e, "name", "") == "player" and e != self.player:
                    self.target = e
                    break
        
        if self.target != None:
            self.data["dx"] = self.target.x - self.player.x
            self.data["dy"] = self.target.y - self.player.y
            self.data["target_attacking"] = getattr(self.target, "is_attacking", False)
            target_pos = self.target.position 
            self.data["target_over_void"] = not raycast(target_pos, Vec3(0, -1, 0), 5, ignore=([self.player] + self.player.team + self.player.enemy)).hit 

    def get_lowest_platform_y(self):
        lowest = 9999
        for e in scene.entities:
            if getattr(e, "name", "") == "solid":
                if e.y < lowest:
                    lowest = e.y
        return lowest

    def is_danger(self):
        if self.level == 1:
            return self.data["void_c"]
        if self.level == 2:
            lowest_y = self.get_lowest_platform_y()
            return self.data["void_c"] and self.player.y < lowest_y
        return False

    def recover(self):
        intentions = {k: 0 for k in self.inputs}
        dx = self.data.get("dx", 0)
        if dx > 0:
            intentions["right"] = 2
        else:
            intentions["left"] = 2

        if self.data["vel_y"] < -1 and self.player.physics.remaining_jump > 0:
            intentions["jump"] = 1
        elif self.data["vel_y"] > 0:
            intentions["jump"] = 2
        return intentions

    def heal(self, dx): 
        intentions = {k: 0 for k in self.inputs}
        going_left = dx > 0 
        
        if going_left:
            border = self.data["void_l"] 
        else: 
            border = self.data["void_r"]
        
        if border: 
            return self.fight(dx, self.data.get("dy", 0))

        if abs(dx) < 7:
            if going_left:
                intentions["left"] = 2
            else: 
                intentions["right"] = 2
        else:
            intentions["interact"] = 1 
        return intentions

    def fight(self, dx, dy): 
        intentions = {k: 0 for k in self.inputs}
        target_in_air = self.data.get("target_over_void", False) 
        
        if dx > 1:
            if not self.data["void_r"] or not target_in_air: 
                intentions["right"] = 2
        elif dx < -1:
            if not self.data["void_l"] or not target_in_air: 
                intentions["left"] = 2
        
        if dy > 2.5 and abs(dx) < 3 and self.data["safe"]: 
            intentions["jump"] = 1

        if abs(dx) < 3 and abs(dy) < 1.5:
            intentions[random.choice(["attack", "play", "dash"])] = 1
        return intentions

    def decide_easy(self):
        intentions = {k: 0 for k in self.inputs}
        dx = self.data.get("dx", 0)
        dy = self.data.get("dy", 0)
        if abs(dx) < 1.5 and abs(dy) < 1:
            intentions["attack"] = 1
            return intentions
        if dx > 0.5:
            intentions["right"] = 2 
            if self.data["void_r"]: 
                intentions["jump"] = 1
        elif dx < -0.5:
            intentions["left"] = 2 
            if self.data["void_l"]: 
                intentions["jump"] = 1
        return intentions

    def decide_medium(self): 
        dx = self.data.get("dx", 0)
        dy = self.data.get("dy", 0)
        
        if self.data.get("target_attacking") and abs(dx) < 2 and self.data["safe"]:
            if random.random() < 0.5: 
                return {"defend": 1}

        if self.player.hp < 50 and random.random() < 0.3: 
            return self.heal(dx)

        return self.fight(dx, dy)

    def decide_hard(self):
        return {k: 0 for k in self.inputs}

    def apply_inputs(self, intentions):
        for k in self.inputs:
            if intentions.get(k, 0) > 0:
                if self.old_inputs[k] == 0:
                    self.inputs[k] = 1
                else:
                    self.inputs[k] = 2
            else:
                self.inputs[k] = 0
        self.old_inputs = self.inputs.copy()
        return self.inputs

    def update(self):
        self.perceive()
        self.timer += time.dt
        
        new_intentions = None
        if self.is_danger():
            new_intentions = self.recover()
            self.timer = 0
        elif self.timer >= self.delay:
            self.timer = 0
            if self.level == 1:
                new_intentions = self.decide_easy()
            elif self.level == 2:
                new_intentions = self.decide_medium()
            elif self.level == 3:
                new_intentions = self.decide_hard()

        if new_intentions != None:
            self.apply_inputs(new_intentions)
        
        self.player.inputManager.inputs = self.inputs