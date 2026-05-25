from ursina import *
from game.manager.input import InputManager
from game.manager.resource import resourceManager
from game.manager.animation import AnimationManager
from game.core.physics import Physics

JumpEnd = resourceManager.picture("kenzo/jump/end/basic")

number_frames = {
    "Idle" : 10,
    "Walk" : 12,
    "Run" : 16,
    "Dash" : 8,
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
    "DashAttack": 6,
    "ThrowAttack": 7,

    "Defend" : 6,
    "Healing" : 15,
    "Hurt" : 4,
    "Death" : 9
}


class Kenzo(Entity):
    def __init__(self, type = "player", facing = "right", team = [], enemy = [], **kwargs):
        super().__init__(
            model="quad", 
            name=type,
            texture= JumpEnd,
            **kwargs
        )
        self.inputManager = InputManager()
        self.type = type
        self.scale_val = (0.15,0.33)
        self.scale=3.5
        self.collider = BoxCollider(self, size=Vec3(self.scale_val[0], self.scale_val[1], 1), center=(0, -0.178, 0))
        self.collider.visible = False
        self.speed_variation = 1
        self.hp = 3
        self.kokoro = 1
        self.kokoro_steal = 0
        self.isDebuging = False
        self.hp_ui = Text(
            text=str(int(self.hp)),
            parent=self,
            position=(0, 0.1, 0),
            scale=4,
            color=color.black
        )
        self.team = team
        self.enemy = enemy

        self.playername = "kenzo"
        self.facing = facing
        self.animManager = AnimationManager(self, self.playername, number_frames)
        self.physics = Physics(self)
        self.currentAnim = self.animManager.animations["JumpEnd"][facing]
        self.currentAnim.loop()
        
    def initstats(self):
        if self.type == "player" :
            self.inputManager.activate = True
            self.z = -1.05
        else:
            self.z = -1
            
    def update(self):
        if self.inputManager.click("debug"):
            self.isDebuging = not self.isDebuging
            self.collider.visible = not self.collider.visible
            for i in range(len(self.enemy)):
                self.enemy[i].isDebuging = not self.enemy[i].isDebuging 
                self.enemy[i].collider.visible = not self.enemy[i].collider.visible
            for i in range(len(self.team)):
                self.team[i].isDebuging = not self.team[i].isDebuging 
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
            self.hp_ui.text = str(int(self.hp))
            