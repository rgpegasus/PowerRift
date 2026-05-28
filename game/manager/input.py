from ursina import mouse, held_keys, time
import keyboard

class InputManager:
    def __init__(self):
        self.key = {
            "left":    "q",
            "right":   "d",
            "up":      "z",
            "dash":    "shift",
            "get off": "s",
            "interact":"e",
            "throw":   "a",
            "defend":  "right mouse",
            "jump":    "space",
            "attack":  "left mouse",
            "play":    "p",
            "debug":   "F1",
        }
        self.gamepad = {
            "left":    ["gamepad dpad left"],
            "right":   ["gamepad dpad right"],
            "up":      ["gamepad dpad up"],
            "dash":    ["gamepad leftstick press", "gamepad leftshoulder"],
            "get off": ["gamepad leftstick down"],
            "interact":["gamepad y"],
            "throw":   ["gamepad x"],
            "defend":  ["gamepad rightshoulder"],
            "jump":    ["gamepad a"],
            "attack":  ["gamepad b"],
            "play":    ["gamepad start"]
        }
        self.inputs = {
            "left": 0, "right": 0, "up": 0, "dash": 0,
            "get off": 0, "interact": 0, "throw": 0,
            "defend": 0, "jump": 0, "attack": 0, "play": 0,
        }
        self.timer = {"left": 0, "right": 0}
        self.prev_state = {}
        self.activate = False
        self.activate_input = True
        # Mettre à True pour un personnage piloté par le réseau :
        # update_inputs() ne lira plus le clavier/souris, seulement self.inputs
        self.network_controlled = False

    def pressed(self, action):
        if self.network_controlled:
            return self.inputs.get(action, 0) >= 1
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
        for k in gamepad:
            if held_keys.get(k):
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
        if self.network_controlled:
            current = self.inputs.get(action, 0) >= 1
            previous = self.prev_state.get(action, False)
            clicked = current and not previous
            self.prev_state[action] = current
            return clicked
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
        for k in gamepad:
            if held_keys.get(k):
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
        clicked = current and not previous
        self.prev_state[action] = current
        return clicked

    def combo_pressed(self, actions):
        for action in actions:
            if not self.inputs[action] != 0:
                return False
        return True

    def no_input(self):
        if self.network_controlled:
            return all(v == 0 for v in self.inputs.values())
        for action in self.key:
            if self.pressed(action):
                return False
        return True

    def update_inputs(self):
        # Mode réseau : les inputs sont déjà injectés depuis 1v1.py, rien à lire
        if self.network_controlled:
            if self.inputs["left"] == 2 and self.inputs["right"] == 2:
                if self.timer["left"] >= self.timer["right"]:
                    self.inputs["left"] = 0
                else:
                    self.inputs["right"] = 0
            return

        if self.activate and self.activate_input:
            for action in self.inputs:
                if self.click(action):
                    self.inputs[action] = 1
                elif self.pressed(action):
                    for direction in ["left", "right"]:
                        if action == direction:
                            self.timer[direction] += time.dt
                    self.inputs[action] = 2
                else:
                    for direction in ["left", "right"]:
                        if action == direction:
                            self.timer[direction] = 0
                    self.inputs[action] = 0
        if self.inputs["left"] == 2 and self.inputs["right"] == 2:
            if self.timer["left"] >= self.timer["right"]:
                self.inputs["left"] = 0
            else:
                self.inputs["right"] = 0