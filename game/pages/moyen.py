from ursina import *
from game.entities.kenzo import Kenzo
from game.manager.resource import resourceManager
from game.manager.map import MapManager
from game.core.AI import AI
from game.core.state import state
from game.core.map_config import build_platforms, MAP_MUSIC

platformTexture = resourceManager.picture("background/map/platform")

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
        self.ai = AI(Kenzo(position=(2, 15, -1)), level=2)
        self.enemy = [self.ai.player]
        self.play = MapManager(self)
        music_key = MAP_MUSIC.get(state.selected_map)
        if music_key:
            self.map_music = resourceManager.music(music_key)
            if self.map_music:
                self.map_music.play()

    def update(self):
        self.ai.update()
