# Permet d'importer le bon fichier facilement
import os
from ursina import load_texture, Audio

class ResourceManager:
    def __init__(self, base_path="game/resources"):
        self.base_path = base_path

    def picture(self, key):
        folder_path = os.path.join(self.base_path, "pictures", os.path.dirname(key)).replace("\\", "/")
        file_name = os.path.basename(key)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if os.path.splitext(file)[0] == file_name:
                    return load_texture(os.path.join(folder_path, file).replace("\\", "/"))
        return None
    
    def icon(self, key):
        folder_path = os.path.join(self.base_path, "icons", os.path.dirname(key)).replace("\\", "/")
        file_name = os.path.basename(key)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if os.path.splitext(file)[0] == file_name:
                    return load_texture(os.path.join(folder_path, file).replace("\\", "/"))
        return None
    
    def effect(self, key):
        folder_path = os.path.join(self.base_path, "sounds/effects", os.path.dirname(key)).replace("\\", "/")
        file_name = os.path.basename(key)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if os.path.splitext(file)[0] == file_name:
                    return Audio(os.path.join(folder_path, file).replace("\\", "/"), autoplay=False)
        return None

    def music(self, key, volume=0.5):
        folder_path = os.path.join(self.base_path, "sounds/music", os.path.dirname(key)).replace("\\", "/")
        file_name = os.path.basename(key)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if os.path.splitext(file)[0] == file_name:
                    return Audio(os.path.join(folder_path, file).replace("\\", "/"), loop=True, volume=volume)
        return None
    
resourceManager = ResourceManager()
