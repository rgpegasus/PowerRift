from ursina import *
from ursina.prefabs.input_field import InputField
from game.manager.resource import resourceManager
from game.manager.page import PageManager
from game.network.manager import Networking
from game.core.engine import engine
from game.core.state import state
import socket

backgroundMap = resourceManager.picture("background/map/background")
hebergerImage = resourceManager.picture("button/heberger")
rejoindreImage = resourceManager.picture("button/rejoindre")
retourImage = resourceManager.picture("button/retour")


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

def get_local_ip():
    """Retourne l'IP LAN réelle (même interface que ipconfig)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

class IpOverlay(Entity):
    def __init__(self, on_confirm):
        super().__init__(parent=camera.ui)
        self.on_confirm = on_confirm

        self.overlay = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 18),
            scale=(2, 2),
            position=(0, 0),
            z=-1
        )
        self.panel = Entity(
            parent=self,
            model='quad',
            color=color.white,
            scale=(0.55, 0.22),
            position=(0, 0),
            z=-2
        )
        self.label = Text(
            parent=self,
            text="adresse IP du serveur :",
            origin=(0, 0),
            position=(0, 0.06),
            scale=1.2,
            color=color.black,
            z=-3
        )
        self.field = InputField(
            parent=self,
            default_value='',
            position=(0, 0),
            scale=(0.4, 0.05),
            z=-3
        )
        self.confirm_btn = Button(
            parent=self,
            text='confirmer',
            color=color.azure,
            scale=(0.15, 0.05),
            position=(0.1, -0.07),
            z=-3,
            on_click=self._confirm
        )
        self.cancel_btn = Button(
            parent=self,
            text='annuler',
            color=color.light_gray,
            scale=(0.15, 0.05),
            position=(-0.1, -0.07),
            z=-3,
            on_click=self._destroy
        )

    def _confirm(self):
        ip = self.field.text.strip()
        if ip:
            self._destroy()
            self.on_confirm(ip)

    def _destroy(self):
        destroy(self)

class Scene(Entity):
    def __init__(self):
        global _client_just_connected
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
        spacing = 0.13

        if engine.netRole and engine.netRole.role == "client":
            self.status_text = Text(
                parent=camera.ui,
                text="Connecté au serveur\nEn attente du choix de map du host...",
                origin=(0, 0),
                position=(0, 0),
                scale=1.5,
                color=color.yellow,
                z=-1
            )
            self.retour = MenuButton(
                texture=retourImage,
                position=(-0.78, 0.43),
                scale=(0.12, 0.12),
                action=lambda: PageManager.load("jouer_menu")
            )
            self.heberger = None
            self.rejoindre = None
            
        elif engine.netRole and engine.netRole.role == "host":
            self.ip_label = Text(
                parent=camera.ui,
                text=get_local_ip(),
                position=(-0.23, 0.4),
                scale=3.0,
                color=color.white,
                z=-1
            )
            
            # Vérifier le nombre RÉEL de clients connectés au serveur
            num_clients = engine.netRole.real_client_count() 
            if num_clients > 0:
                status_msg = "Client connecté!\nClique pour choisir une map"
                btn_enabled = True
            else:
                status_msg = "Serveur créé\nEn attente d'un client..."
                btn_enabled = False
            
            self.status_text = Text(
                parent=camera.ui,
                text=status_msg,
                origin=(0, 0),
                position=(0, 0),
                scale=1.5,
                color=color.yellow,
                z=-1
            )
            
            self.continuer_btn = Button(
                parent=camera.ui,
                text='Choisir une map',
                color=color.dark_gray,
                scale=(button_scale[0] * 0.8, button_scale[1] * 0.6),
                position=(0, -spacing),
                z=0,
                on_click=lambda: self._go_to_map_select()
            )
            self.continuer_btn.enabled = btn_enabled
            
            self.retour = MenuButton(
                texture=retourImage,
                position=(-0.78, 0.43),
                scale=(0.12, 0.12),
                action=lambda: PageManager.load("jouer_menu")
            )
            self.heberger = None
            self.rejoindre = None
            
            # Ne pas créer un nouveau Networking s'il existe déjà (créé par _serverSetting)
            # Il sera créé par _serverSetting avant le rechargement de la page
            
        else:
            self.heberger = MenuButton(
                texture=hebergerImage,
                position=(0, spacing),
                scale=button_scale,
                action=lambda: self._serverSetting("host")
            )
            self.rejoindre = MenuButton(
                texture=rejoindreImage,
                position=(0, -spacing),
                scale=button_scale,
                action=lambda: self._serverSetting("client")
            )
            self.retour = MenuButton(
                texture=retourImage,
                position=(-0.78, 0.43),
                scale=(0.12, 0.12),
                action=lambda: PageManager.load("jouer_menu")
            )
            self.status_text = None
            self.continuer_btn = None

    def _serverSetting(self, role):
        if role == "host":
            engine.netRole = Networking(
                "host",
                on_client_connected=lambda: PageManager.load("server")
            )
            PageManager.load("server")
        else:
            IpOverlay(on_confirm=self._connectAsClient)

    def _connectAsClient(self, ip):
        state.game_mode = "1v1"
        state.back_page = "jouer_menu"
        engine.netRole = Networking("client", ip)
        PageManager.load("server")

    def _go_to_map_select(self):
        state.game_mode = "1v1"
        state.back_page = "jouer_menu"
        PageManager.load("map_select")


