# Permet de changer de page
from ursina import destroy, scene
from importlib import import_module

class PageManager:
    current_scene = None
    scene_entities = []

    @staticmethod
    def load(name):
        for e in PageManager.scene_entities:
            if e:
                destroy(e)
        PageManager.scene_entities.clear()
        module = import_module(f"game.pages.{name}")
        PageManager.current_scene = module.Scene()
        new_entities = []

        for e in scene.entities:
            if e != PageManager.current_scene:
                new_entities.append(e)

        PageManager.scene_entities = [PageManager.current_scene] + new_entities
