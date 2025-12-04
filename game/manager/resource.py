# Charge tous les fichiers dans game/resources/** et les classe selon leur type.
import os
from ursina import load_texture, Audio


class ResourceManager:
    def __init__(self, base_path="../resources"):
        self.base_path = base_path

        self.pictures = {}
        self.sounds = {}
        self.musics = {}

        self.load_all()

    def load_all(self):
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                path = os.path.join(root, file).replace("\\", "/")
                if (path.find("sounds-effects") != -1) :
                    # SOUNDS
                    index = path.find("sounds-effects")
                    key = path[:index-1] + path[index+14:] \
                        .replace(self.base_path + "/", "") \
                        .replace("/", "_") \
                        .replace(".", "_")
                    self.sounds[key] = path 
                elif (path.find("music") != -1) :
                    # MUSICS
                    index = path.find("music") 
                    key = path[:index-1] + path[index+5:] \
                        .replace(self.base_path + "/", "") \
                        .replace("/", "_") \
                        .replace(".", "_")
                    self.musics[key] = path
                else :
                    # PICTURES
                    key = path \
                        .replace(self.base_path + "/", "") \
                        .replace("/", "_") \
                        .replace(".", "_")
                    self.pictures[key] = load_texture(path)
                    

    def picture(self, key):
        return self.pictures.get(key, None)

    def sound(self, key):
        return Audio(self.sounds.get(key), autoplay=False)

    def music(self, key, volume=0.5):
        return Audio(self.musics.get(key), loop=True, volume=volume)


resourceManager = ResourceManager()
