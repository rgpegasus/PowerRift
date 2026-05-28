from ursina import *
from game.entities.kenzo import Kenzo
from game.manager.resource import resourceManager
from game.manager.page import PageManager


class MapManager(Entity):
    def __init__(self, map):
        super().__init__()
        self.map = map
        invoke(self.init_characters, delay=0.5)
        camera.orthographic = True
        camera.fov = 10
        self.player = None
        self.enemy = None
        self.team = None
        self.entities = []
        self.initialized = False
        self.game_over = False

    def init_characters(self):
        self.player = self.map.player
        self.team = self.map.team
        self.enemy = self.map.enemy
        self.player.enemy = self.enemy
        self.player.team = self.team
        self.player.initstats()
        for t in self.team:
            t.type = "team"
            t.team = [self.player]
            t.enemy = self.player.enemy
            for x in self.team:
                if x != t:
                    t.team.append(x)
            t.initstats()
        for e in self.enemy:
            if e.type != "AI":
                e.type = "enemy"
            e.facing = "left"
            e.enemy = [self.player] + self.team
            for x in self.enemy:
                if x != e:
                    e.team.append(x)
            e.initstats()
        self.entities = [self.player] + self.team + self.enemy
        self.initialized = True

    def _trigger_end_game(self):
        if self.game_over:
            return
        self.game_over = True

        self.overlay = Entity(
            parent=camera.ui,
            model='quad',
            color=color.black,
            scale=(4, 4),
            z=-0.5,
        )
        self.overlay.alpha = 0
        self.overlay.animate('alpha', 0.68, duration=1.5)
        camera.animate('fov', 6.5, duration=1.5)
        invoke(self._show_end_buttons, delay=1.6)

    def _show_end_buttons(self):
        menuPrincipalImg = resourceManager.picture("button/menu_principal")
        quitterImg = resourceManager.picture("button/quitter")
        self.menu_btn = Entity(
            parent=camera.ui,
            model='quad',
            texture=menuPrincipalImg,
            position=(0, 0.11),
            scale=(0.65, 0.325),
            collider='box',
            z=-1,
        )
        self.menu_btn.on_mouse_enter = lambda: self.menu_btn.animate('alpha', 0.55, duration=0.1)
        self.menu_btn.on_mouse_exit  = lambda: self.menu_btn.animate('alpha', 1.0,  duration=0.1)
        self.quit_btn = Entity(
            parent=camera.ui,
            model='quad',
            texture=quitterImg,
            position=(0, -0.11),
            scale=(0.66, 0.175),
            collider='box',
            z=-1,
        )

    def _destroy_end_ui(self):
        for attr in ('overlay', 'menu_btn', 'quit_btn'):
            e = getattr(self, attr, None)
            if e:
                try:
                    destroy(e)
                except Exception:
                    pass

    def input(self, key):
        if key == 'left mouse down' and self.game_over and hasattr(self, 'menu_btn'):
            if self.menu_btn.hovered:
                self._destroy_end_ui()
                camera.fov = 10
                PageManager.load("menu")
            elif self.quit_btn.hovered:
                application.quit()

    def update(self):
        if self.player is not None:
            if self.player.inputManager.click("debug"):
                for platform in self.map.platforms:
                    platform.visible = not platform.visible

            if self.player.x > -5 and self.player.x < 5:
                camera.x = self.player.x
            if self.player.y > -2.5 and self.player.y <= 2.5:
                camera.y = self.player.y
            elif self.player.y > 2.5:
                camera.y = 2.5
            i = 0
            while i < len(self.entities):
                if self.entities[i].y <= -20 or self.entities[i].y >= 20 or self.entities[i].x <= -5 and self.entities[i].x >= 5:
                    self.entities[i].hp -= 1
                    if self.entities[i].hp > 0:
                        self.entities[i].position = (0, 10)
                        self.entities[i].physics.velocity_y = 0
                        self.entities[i].physics.velocity_x = 0
                        self.entities[i].kokoro = 1
                        self.entities[i].physics.knockback = Vec3(0, 0, 0)
                        self.entities[i].inputManager.activate_input = True
                    else:
                        if self.entities[i].type == "player":
                            self.player = None
                            self.entities.pop(i)
                            i -= 1
                        elif self.entities[i].type == "team":
                            for y in range(len(self.team)):
                                if self.team[y] == self.entities[i]:
                                    self.team.pop(y)
                                    self.entities.pop(i)
                                    i -= 1
                                    break
                        else:
                            for y in range(len(self.enemy)):
                                if self.enemy[y] == self.entities[i]:
                                    self.enemy.pop(y)
                                    self.entities.pop(i)
                                    i -= 1
                                    break
                i += 1

        if self.initialized and not self.game_over:
            if self.player is None or len(self.enemy) == 0:
                self._trigger_end_game()
