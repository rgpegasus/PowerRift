from ursina import *
from game.manager.resource import resourceManager
from game.manager.page import PageManager
from game.core.state import state
from game.core.engine import engine

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

_BORDER = 0.014

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
            self._alive = False
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

        is_host = engine.netRole and engine.netRole.role == "host"

        if is_host:
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
            self.waiting_text = None

        else:
            self.waiting_text = Text(
                parent=camera.ui,
                text="En attente du choix de map du host...",
                origin=(0, 0),
                position=(0, 0),
                scale=2,
                color=color.white,
                z=-1
            )
            self.cards = []
            self.retour = None

    def _select_map(self, map_name):
        if not (engine.netRole and engine.netRole.role == "host"):
            return

        state.selected_map = map_name

        # Détruire les cartes et afficher un message d'attente
        for card in self.cards:
            card._alive = False
            destroy(card._border)
            destroy(card)
        self.cards = []

        self.waiting_text = Text(
            parent=camera.ui,
            text="En attente que le client charge la map...",
            origin=(0, 0),
            position=(0, 0),
            scale=2,
            color=color.yellow,
            z=-1
        )

        # Le host charge le jeu UNIQUEMENT après avoir reçu l'ACK du client
        engine.netRole.on_ready = lambda: PageManager.load(state.game_mode)
        engine.netRole.send_map_selection(map_name)

    def input(self, key):
        if key == 'left mouse down' and self.retour and self.retour.hovered:
            PageManager.load(state.back_page)