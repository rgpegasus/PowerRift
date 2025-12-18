from ursina import mouse, held_keys
import keyboard
class InputManager:
    def __init__(self):
        self.key = {
            "left": "q",
            "right": "d",
            "up": "z",
            "get off": "s",
            "defend": "right mouse",
            "jump": "space",
            "attack": "left mouse",
            "play": "p"
        }
        self.gamepad = {
            "left": ["gamepad dpad left"],
            "right": ["gamepad dpad right"],
            "up": ["gamepad dpad up"],
            "get off": ["gamepad dpad down"],
            "defend": ["gamepad x"],
            "jump": ["gamepad a"],
            "attack": ["gamepad b"],
            "play": ["gamepad start"]
        }
        self.prev_state = {}

    def pressed(self, action):
        key = self.key.get(action)
        if not key:
            return False
        if key == "left mouse":
            return mouse.left
        elif key == "right mouse":
            return mouse.right
        elif keyboard.is_pressed(key):
            return True

        gamepad = self.gamepad.get(action, [])
        for key in gamepad:
            if held_keys.get(key):
                return True

        if action == "left":
            return held_keys.get("gamepad left stick x", 0) < -0.5
        elif action == "right":
            return held_keys.get("gamepad left stick x", 0) > 0.5
        elif action == "up":
            return held_keys.get("gamepad left stick y", 0) > 0.5
        elif action == "get off":
            return held_keys.get("gamepad left stick y", 0) < -0.5
        
        return False
    
    def click(self, action):
        key = self.key.get(action)
        current = False
        if not key:
            return False
        if key == "left mouse":
            current = mouse.left
        elif key == "right mouse":
            current = mouse.right
        elif keyboard.is_pressed(key):
            current = True

        gamepad = self.gamepad.get(action, [])
        for key in gamepad:
            if held_keys.get(key):
                current = True
        if not current:
            if action == "left":
                current = held_keys.get("gamepad left stick x", 0) < -0.5
            elif action == "right":
                current = held_keys.get("gamepad left stick x", 0) > 0.5
            elif action == "up":
                return held_keys.get("gamepad left stick y", 0) > 0.5
            elif action == "get off":
                current = held_keys.get("gamepad left stick y", 0) < -0.5

        previous = self.prev_state.get(action, False)
        if current:
            if not previous:
                clicked = True
            else:
                clicked = False
        else:
            clicked = False
        self.prev_state[action] = current

        return clicked
    
    def combo_pressed(self, actions):
        for action in actions:
            if not self.pressed(action):
                return False
        return True


inputManager = InputManager()
