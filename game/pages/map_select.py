from ursina import *
from game.manager.resource import resourceManager
from game.manager.page import PageManager
from game.core.state import state

_bgImg   = resourceManager.picture("background/map/background")
_map1Img = resourceManager.picture("background/map/background")
_map2Img = resourceManager.picture("background/map/map2")
_map3Img = resourceManager.picture("background/map/map3")
_retourImg = resourceManager.picture("button/retour")

MAPS = [
    ("background", _map1Img),
    ("map2",       _map2Img),
    ("map3",       _map3Img),
]


_BORDER = 0.014   # épaisseur de la bordure

class MapCard(Entity):
    def __init__(self, map_name, texture, x, on_select):
        super().__init__(
            parent=camera.ui,
            model='quad',
            texture=texture,
            position=(x, 0),
            scale=(0.48, 0.30),
            collider='box',
            z=0,
        )
        self.map_name = map_name
        self.on_select = on_select
        self._alive = True

        self._border = Entity(
            parent=camera.ui,
            model='quad',
            color=color.white,
            alpha=0,
            position=(x, 0),
            scale=(0.48 + _BORDER * 2, 0.30 + _BORDER * 2),
            z=0.01,
        )

    def on_mouse_enter(self):
        if not self._alive:
            return
        try:
            self.animate('scale_x', 0.52, duration=0.1)
            self.animate('scale_y', 0.325, duration=0.1)
            self.animate('alpha', 0.72, duration=0.1)
            self._border.animate('scale_x', 0.52 + _BORDER * 2, duration=0.1)
            self._border.animate('scale_y', 0.325 + _BORDER * 2, duration=0.1)
            self._border.animate('alpha', 1.0, duration=0.15)
        except Exception:
            pass

    def on_mouse_exit(self):
        if not self._alive:
            return
        try:
            self.animate('scale_x', 0.48, duration=0.1)
            self.animate('scale_y', 0.30, duration=0.1)
            self.animate('alpha', 1.0, duration=0.1)
            self._border.animate('scale_x', 0.48 + _BORDER * 2, duration=0.1)
            self._border.animate('scale_y', 0.30 + _BORDER * 2, duration=0.1)
            self._border.animate('alpha', 0.0, duration=0.15)
        except Exception:
            pass

    def input(self, key):
        if self._alive and self.hovered and key == 'left mouse down':
            self._alive = False   # empêche on_mouse_exit de crasher après destroy
            self.on_select(self.map_name)


class Scene(Entity):
    def __init__(self):
        super().__init__()

        Entity(
            parent=camera.ui,
            model='quad',
            texture=_bgImg,
            scale=(camera.aspect_ratio, 1),
            z=1,
        )

        xs = [-0.52, 0.0, 0.52]
        self.cards = []
        for i, (map_name, tex) in enumerate(MAPS):
            card = MapCard(map_name, tex, xs[i], self._select_map)
            self.cards.append(card)

        self.retour = Entity(
            parent=camera.ui,
            model='quad',
            texture=_retourImg,
            position=(-0.78, 0.43),
            scale=(0.12, 0.12),
            collider='box',
            z=0,
        )

    def _select_map(self, map_name):
        state.selected_map = map_name
        PageManager.load(state.game_mode)

    def input(self, key):
        if key == 'left mouse down' and self.retour.hovered:
            PageManager.load(state.back_page)
