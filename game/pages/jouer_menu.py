from ursina import *
from game.manager.resource import resourceManager
from game.manager.page import PageManager
from game.core.engine import engine
import socket

backgroundMap = resourceManager.picture("background/map/fond2")
uncontreunImage = resourceManager.picture("button/1v1")
deuxcontredeuxImage = resourceManager.picture("button/2v2")
entrainementImage = resourceManager.picture("button/entrainement")
retourImage = resourceManager.picture("button/retour")

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)


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

        self.uncontreun = MenuButton(
            texture=uncontreunImage,
            position=(0, spacing),
            scale=(0.775, 0.16),
            action=lambda: PageManager.load("1v1")
        )

        self.deuxcontredeux = MenuButton(
            texture=deuxcontredeuxImage,
            position=(0, 0),
            scale=button_scale,
            action=lambda: PageManager.load("2v2")
        )

        self.entrainement = MenuButton(
            texture=entrainementImage,
            position=(0, -spacing),
            scale=button_scale,
            action=lambda: PageManager.load("entrainement")
        )

        self.retour = MenuButton(
            texture=retourImage,
            position=(-0.78, 0.43),
            scale=(0.12, 0.12),
            action=lambda: PageManager.load("server")
        )

        if engine.netRole and engine.netRole.role == "host":
            self.ip_label = Text(
                parent=camera.ui,
                text=ip,
                position=(-0.23, 0.4),
                scale=3.0,
                color=color.white,
                z=-1
            )