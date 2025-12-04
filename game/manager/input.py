# Permet de gérer toutes les actions liés aux touches 
from ursina import mouse
import keyboard

class InputManager:
    def pressed(self, action):
        list = {
            "left" : "q",
            "right" : "d",
            "down" : "s",
            "jump" : "space",
            "attack": "left mouse",
        }

        key = list.get(action)
        if not key:
            return False

        if key == "left mouse":
            return mouse.left
        elif key == "right mouse":
            return mouse.right
        
        return keyboard.is_pressed(key)

inputManager = InputManager()
