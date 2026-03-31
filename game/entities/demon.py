from ursina import *
from game.manager.input import InputManager
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
    def __init__(self, type = "player", facing = "right", team = [], enemy = [],**kwargs):
        super().__init__(
            model="quad", 
            name=type,
            texture= Idle,
            **kwargs
        )
        self.inputManager = InputManager()
        if type == "player" :
            self.inputManager.activate = True
        self.scale_val = (0.18,0.45)
        self.scale=2.6
        self.collider = BoxCollider(self, size=Vec3(self.scale_val[0], self.scale_val[1], 1), center=(0, -0.16, 0))
        self.collider.visible = False
        self.speed_variation = 1
        self.hp = 3
        self.kokoro = 1
        self.hp_ui = Text(
            text=str(int(self.hp)),
            parent=self,
            position=(0, 0.1, 0),
            scale=4,
            color=color.black
        )
        self.team = team
        self.enemy = enemy
        if type == "player":
            self.z = -1.05
        else:
            self.z = -1

        self.playername = "demon"
        self.facing = facing
        self.animManager = AnimationManager(self, self.playername, number_frames)
        self.physics = Physics(self)
        self.currentAnim = self.animManager.animations["Idle"][facing]
        self.currentAnim.loop()
        

    def update(self):
        if self.inputManager.click("debug"):
            self.collider.visible = not self.collider.visible
            for i in range(len(self.enemy)):
                self.enemy[i].collider.visible = not self.enemy[i].collider.visible
            for i in range(len(self.team)):
                self.team[i].collider.visible = not self.team[i].collider.visible
        all_attack_collider = []
        for e in self.enemy:
            if e.physics.attack_collider != None:
                all_attack_collider.append(e.physics.attack_collider)
        for e in self.team:
            if e.physics.attack_collider != None:
                all_attack_collider.append(e.physics.attack_collider)
        if self.physics.attack_collider != None:
            all_attack_collider.append(self.physics.attack_collider)
        self.physics.ignore = self.enemy + self.team + all_attack_collider
        self.physics.update()
        self.animManager.update()
        if self.hp_ui.text != "":
            self.hp_ui.text=str(int(self.hp))
