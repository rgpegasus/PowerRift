from ursina import *
from game.entities.kenzo import Kenzo
from game.manager.resource import resourceManager
from game.manager.page import PageManager
from game.manager.map import MapManager
from game.core.engine import engine
import time
from game.core.state import state
from game.core.map_config import build_platforms, MAP_MUSIC

platformTexture = resourceManager.picture("background/map/platform")

SEND_RATE = 0.066  # ~15 Hz (66ms) — réduit la bande passante
SNAP_THRESHOLD = 3.0  # Augmenté pour éviter les téléportations fréquentes
INTERPOLATION_FACTOR = 0.8  # Plus agressif pour lissage (0.4 → 0.8)


class Scene(Entity):
    def __init__(self):
        super().__init__()
        backgroundMap = resourceManager.picture(f"background/map/{state.selected_map}")
        self.background = Entity(z=2, model='quad', texture=backgroundMap, scale=(30, 15), position=(0, 0))
        if state.selected_map == "background":
            Entity(z=1.5, model='quad', texture=platformTexture, scale=(20, 12), position=(0, 0))
        self.platforms = build_platforms(state.selected_map)
        self.player = Kenzo(position=(-2, 15, -1))
        self.team = []
        self.enemy = [Kenzo(position=(2, 15, -1))]
        self.play = MapManager(self)
        self.map_music = None
        self.current_map = None
        self.net = engine.netRole
        self.last_send = 0
        # Garde les inputs reçus au tick précédent pour détecter les fronts montants
        self._prev_enemy_inputs = {}
        # Stocke la dernière position reçue pour prédiction
        self._last_enemy_pos = {"x": 0, "y": 0}
        self._last_enemy_vel = {"x": 0, "y": 0}

        if self.net:
            print(f"[1v1] Partie lancée — id: {self.net.my_id} | rôle: {self.net.role}")
            self.player.net = self.net
            self.enemy[0].inputManager.activate = True
            self.enemy[0].inputManager.network_controlled = True
            if self.net.role == "host":
                self.player.position = (-2, 15, -1)
                self.enemy[0].position = (2, 15, -1)
            else:
                self.player.position = (2, 15, -1)
                self.enemy[0].position = (-2, 15, -1)

    def _apply_enemy_inputs(self, enemy, received):
        """
        Injecte les inputs reçus dans l'InputManager de l'ennemi.
        Les valeurs "1" (click) sont reconstituées en comparant avec le tick précédent :
        un input passe à 1 quand il vient de passer de 0 à !=0.
        """
        prev = self._prev_enemy_inputs
        merged = {}
        for action, value in received.items():
            prev_val = prev.get(action, 0)
            if value != 0 and prev_val == 0:
                # Front montant → click
                merged[action] = 1
            else:
                merged[action] = value
        self._prev_enemy_inputs = dict(received)
        enemy.inputManager.inputs = merged

    def update(self):
        if not self.net:
            return

        if self.net.opponent_disconnected:
            print("[1v1] Adversaire déconnecté — retour au menu")
            self.net.opponent_disconnected = False
            engine.netRole = None
            PageManager.load("jouer_menu")
            return

        now = time.time()

        # Envoyer les inputs à une fréquence réduite (~15 Hz)
        if now - self.last_send >= SEND_RATE:
            self.net.send("server_inputs", {
                "inputs": dict(self.player.inputManager.inputs),
                "facing": self.player.facing,
                "x":      self.player.x,
                "y":      self.player.y,
            })
            self.last_send = now

        # Appliquer un hit reçu sur le joueur local
        if self.net.pending_hit:
            hit = self.net.pending_hit
            self.net.pending_hit = None
            self.player.physics.knockback = Vec3(hit["knockback_x"], hit["knockback_y"], 0)
            self.player.physics.timer = 0
            self.player.kokoro = hit["kokoro"]
            self.player.animManager.play("Hurt", "play")

        # Injection inputs + recalage position ennemi distant avec interpolation améliorée
        my_id = self.net.my_id
        for player_id, data in self.net.ennemis.items():
            if my_id is not None and player_id == my_id:
                continue
            enemy = self.enemy[0]

            self._apply_enemy_inputs(enemy, data["inputs"])

            # Calculer la distance de divergence
            dx = data["x"] - enemy.x
            dy = data["y"] - enemy.y
            distance = (dx**2 + dy**2)**0.5

            # Calculer la vélocité estimée pour prédiction
            vel_x = data["x"] - self._last_enemy_pos["x"]
            vel_y = data["y"] - self._last_enemy_pos["y"]

            if distance > SNAP_THRESHOLD:
                # Snap seulement si trop loin (lag/désync majeur)
                enemy.x = data["x"]
                enemy.y = data["y"]
                enemy.physics.velocity_x = 0
                enemy.physics.velocity_y = 0
                enemy.physics.knockback = Vec3(0, 0, 0)
                print(f"[1v1] SNAP — distance={distance:.2f}")
            else:
                # Interpolation lissée avec coefficient plus agressif
                enemy.x += dx * INTERPOLATION_FACTOR
                enemy.y += dy * INTERPOLATION_FACTOR

            # Sauvegarder pour prédiction au prochain tick
            self._last_enemy_pos = {"x": data["x"], "y": data["y"]}
            self._last_enemy_vel = {"x": vel_x, "y": vel_y}
            break
        music_key = MAP_MUSIC.get(state.selected_map)
        if music_key and self.current_map != music_key:
            if self.map_music:
                self.map_music.stop()

            self.map_music = resourceManager.music(music_key)
            self.current_map = music_key
