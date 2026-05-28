from ursina import *
from game.manager.resource import resourceManager
from game.manager.page import PageManager

backgroundMap = resourceManager.picture("background/map/background")
jouerImage = resourceManager.picture("button/jouer")
optionImage = resourceManager.picture("button/option")
quitterImage = resourceManager.picture("button/quitter")

class MenuButton(Entity):
    def __init__(self, texture, position=(0, 0), scale=(0.625, 0.18), action=None):
        super().__init__(
            parent=camera.ui,
            model='quad',
            texture=texture,
            position=position,
            scale=scale,
            collider='box',
            z=0
        )
        self.default_alpha = 1
        self.hover_alpha = 0.6
        self.action = action

    def on_mouse_enter(self):
        self.animate('alpha', self.hover_alpha, duration=0.1)

    def on_mouse_exit(self):
        self.animate('alpha', self.default_alpha, duration=0.1)

    def input(self, key):
        if self.hovered and key == 'left mouse down' and self.action:
            self.action()

class Scene(Entity):
    def __init__(self):
        super().__init__()

        self.background = Entity(
            parent=camera.ui,
            model='quad',
            texture=backgroundMap,
            scale=(camera.aspect_ratio, 1),
            position=(0, 0),
            z=1
        )

        button_scale = (0.625, 0.18)
        spacing = 0.18

        self.jouer = MenuButton(
            texture=jouerImage,
            position=(0, spacing),
            scale=button_scale,
            action=lambda: PageManager.load("jouer_menu")
        )

        self.option = MenuButton(
            texture=optionImage,
            position=(0, 0),
            scale=button_scale,
            action=lambda: PageManager.load("options")
        )

        self.quitter = MenuButton(
            texture=quitterImage,
            position=(0, -spacing),
            scale=button_scale,
            action=application.quit
        )