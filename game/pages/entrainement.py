from ursina import *
from game.manager.resource import resourceManager
from game.manager.page import PageManager
from game.core.state import state

backgroundMap = resourceManager.picture("background/map/fond2")
facileImage = resourceManager.picture("button/facile")
moyenImage = resourceManager.picture("button/moyen")
difficileImage = resourceManager.picture("button/difficile")
retourImage = resourceManager.picture("button/retour")


def _load_map_select(game_mode):
    state.game_mode = game_mode
    state.back_page = "entrainement"
    PageManager.load("map_select")


class MenuButton(Entity):
    def __init__(self, texture, position=(0, 0), scale=(0.625, 0.16), action=None):
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

        button_scale = (0.700, 0.16)
        spacing = 0.17

        self.facile = MenuButton(
            texture=facileImage,
            position=(0, spacing),
            scale=(0.7, 0.14),
            action=lambda: _load_map_select("facile")
        )

        self.moyen = MenuButton(
            texture=moyenImage,
            position=(0, 0),
            scale=button_scale,
            action=lambda: _load_map_select("moyen")
        )

        self.difficile = MenuButton(
            texture=difficileImage,
            position=(0, -spacing),
            scale=(0.750, 0.19),
            action=lambda: _load_map_select("difficile")
        )

        self.retour = MenuButton(
            texture=retourImage,
            position=(-0.78, 0.43),
            scale=(0.12, 0.12),
            action=lambda: PageManager.load("jouer_menu")
        )
