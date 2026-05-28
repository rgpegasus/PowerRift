from ursina import *
from game.manager.page import PageManager
from game.manager.input import DEFAULT_KEYS, save_keybindings, load_keybindings
from game.manager.resource import resourceManager
from game.core.state import state
import builtins

_bgImg = resourceManager.picture("background/map/background")

ACTIONS = [
    ("left",     "Gauche"),
    ("right",    "Droite"),
    ("jump",     "Sauter"),
    ("up",       "Haut"),
    ("dash",     "Dash"),
    ("get off",  "Descendre"),
    ("attack",   "Attaquer"),
    ("defend",   "Defendre"),
    ("throw",    "Lancer"),
    ("interact", "Interagir"),
]

_KEY_DISPLAY = {
    "left mouse": "Clic G.", "right mouse": "Clic D.",
    "space": "Espace", "shift": "Maj",
    "left shift": "Maj G.", "right shift": "Maj D.",
    "left ctrl": "Ctrl G.", "right ctrl": "Ctrl D.",
    "escape": "Echap", "backspace": "Ret.Arr", "tab": "Tab",
    "enter": "Entree", "delete": "Suppr",
    "up": "Fl.Haut", "down": "Fl.Bas",
    "left": "Fl.Gauche", "right": "Fl.Droite",
}

def _key_label(k):
    return _KEY_DISPLAY.get(k, k.upper())


# ── Slider ────────────────────────────────────────────────────────────────────

class Slider(Entity):
    """Slider glissable dans camera.ui."""

    BAR_W = 0.32
    BAR_H = 0.006

    def __init__(self, label, value, y, x_center=0.08, on_change=None):
        super().__init__(parent=camera.ui, z=-0.3)
        self._x0      = x_center - self.BAR_W / 2
        self._x_center = x_center
        self.value    = value
        self._on_change = on_change
        self._active  = False

        # Libellé à gauche
        Text(parent=camera.ui, text=label,
             position=(self._x0 - 0.06, y),
             scale=1.2, color=color.white, origin=(0.5, 0), z=-2)

        # Piste (zone cliquable + fond visuel)
        self._track = Entity(
            parent=camera.ui, model='quad',
            color=color.gray, alpha=0.4,
            position=(x_center, y),
            scale=(self.BAR_W, self.BAR_H),
            collider='box', z=-0.31,
        )

        # Remplissage coloré
        t  = value / 100.0
        fw = max(0.001, self.BAR_W * t)
        self._fill = Entity(
            parent=camera.ui, model='quad',
            color=color.azure,
            position=(self._x0 + fw / 2, y),
            scale=(fw, self.BAR_H * 1.5), z=-0.35,
        )

        # Poignée (cercle)
        self._handle = Entity(
            parent=camera.ui, model='sphere',
            color=color.white,
            position=(self._x0 + t * self.BAR_W, y),
            scale=(0.026, 0.026, 0.026),
            collider='box', z=-0.40,
        )

        # Valeur à droite
        self._val_text = Text(
            parent=camera.ui, text=f"{value}%",
            position=(x_center + self.BAR_W / 2 + 0.055, y),
            scale=1.2, color=color.white, origin=(-0.5, 0), z=-2,
        )

    # Début du drag en cliquant sur la piste ou la poignée
    def input(self, key):
        if key == 'left mouse down' and (self._track.hovered or self._handle.hovered):
            self._active = True
            self._update_from_mouse()
        elif key == 'left mouse up':
            self._active = False

    def update(self):
        if self._active:
            if mouse.left:
                self._update_from_mouse()
            else:
                self._active = False

    def _update_from_mouse(self):
        t = (mouse.x - self._x0) / self.BAR_W
        t = max(0.0, min(1.0, t))
        new_val = round(t * 100)
        if new_val == self.value:
            return
        self.set_value(new_val)

    def set_value(self, new_val):
        new_val = max(0, min(100, new_val))
        self.value = new_val
        t = new_val / 100.0
        fw = max(0.001, self.BAR_W * t)
        self._fill.scale_x = fw
        self._fill.x       = self._x0 + fw / 2
        self._handle.x     = self._x0 + t * self.BAR_W
        self._val_text.text = f"{new_val}%"
        if self._on_change:
            self._on_change(new_val)


# ── Ligne de remapping ────────────────────────────────────────────────────────

class KeyBindRow:
    def __init__(self, action, label_text, key, lx, bx, y, on_select):
        self.action = action
        self.is_listening = False
        _self = self

        self.label = Text(
            parent=camera.ui, text=label_text,
            position=(lx, y), scale=1.25,
            color=color.white, origin=(-0.5, 0), z=-1,
        )
        self.btn = Button(
            parent=camera.ui,
            text=_key_label(key),
            color=color.gray,
            highlight_color=color.white,
            position=(bx, y),
            scale=(0.165, 0.046),
            z=-0.5,
            on_click=lambda: on_select(_self),
        )
        try:
            self.btn.text_entity.scale *= 0.72
        except Exception:
            pass

    def set_key(self, key):
        self.btn.text = _key_label(key)
        self.set_listening(False)

    def set_listening(self, listening):
        self.is_listening = listening
        self.btn.color = color.orange if listening else color.gray
        if listening:
            self.btn.text = '...'


# ── Page Options ──────────────────────────────────────────────────────────────

class Scene(Entity):
    def __init__(self):
        super().__init__()
        self.bindings      = load_keybindings()
        self.listening_row = None
        self.rows          = []

        # ── Fond flouté (copies décalées simulant le flou) ────
        _offsets = [
            (0,      0,      1,    1.00),
            (0.003,  0.003,  0.98, 0.25),
            (-0.003, 0.003,  0.98, 0.25),
            (0.003, -0.003,  0.98, 0.25),
            (-0.003,-0.003,  0.98, 0.25),
            (0.006,  0,      0.96, 0.18),
            (-0.006, 0,      0.96, 0.18),
            (0,      0.006,  0.96, 0.18),
            (0,     -0.006,  0.96, 0.18),
        ]
        for ox, oy, z, a in _offsets:
            Entity(parent=camera.ui, model='quad', texture=_bgImg,
                   scale=(camera.aspect_ratio, 1),
                   position=(ox, oy), alpha=a, z=z)
        Entity(parent=camera.ui, model='quad',
               color=color.rgba(0, 0, 0, 185),
               scale=(camera.aspect_ratio + 1, 2), z=0.9)

        # ── Titre ──────────────────────────────────────────────
        Text(parent=camera.ui, text="OPTIONS",
             position=(0, 0.43), scale=2.0,
             color=color.white, origin=(0, 0), z=-2)

        # ── Touches ────────────────────────────────────────────
        col = [(-0.42, -0.105), (0.04, 0.365)]
        y0, dy = 0.30, 0.085

        for i, (action, lbl) in enumerate(ACTIONS):
            c, r = i // 5, i % 5
            lx, bx = col[c]
            key = self.bindings.get(action, DEFAULT_KEYS.get(action, "?"))
            self.rows.append(KeyBindRow(action, lbl, key, lx, bx, y0 - r * dy, self.select_row))

        # ── Slider son ────────────────────────────────────────
        self.vol_slider = Slider("Son", state.volume, y=-0.14, on_change=self._vol_changed)

        # ── Boutons bas ────────────────────────────────────────
        Button(parent=camera.ui, text="REINITIALISER",
               color=color.red,   position=(-0.185, -0.385),
               scale=(0.28, 0.050), z=-0.5, on_click=self.reset_bindings)
        Button(parent=camera.ui, text="RETOUR",
               color=color.azure, position=( 0.185, -0.385),
               scale=(0.22, 0.050), z=-0.5,
               on_click=lambda: PageManager.load("menu"))

    # ── Remapping ─────────────────────────────────────────────────────────────

    def select_row(self, row):
        # Double-clic sur la même touche → assigner clic gauche
        if self.listening_row is row:
            self._apply_key('left mouse')
            return
        if self.listening_row:
            self.listening_row.set_listening(False)
        self.listening_row = row
        row.set_listening(True)

    def _apply_key(self, mapped):
        self.bindings[self.listening_row.action] = mapped
        self.listening_row.set_key(mapped)
        save_keybindings(self.bindings)
        self.listening_row = None

    def reset_bindings(self):
        self.bindings = dict(DEFAULT_KEYS)
        save_keybindings(self.bindings)
        for r in self.rows:
            r.set_key(self.bindings.get(r.action, "?"))
        if self.listening_row:
            self.listening_row.set_listening(False)
            self.listening_row = None
        self.vol_slider.set_value(100)

    # ── Son / Luminosité ──────────────────────────────────────────────────────

    def _vol_changed(self, val):
        state.volume = val
        try:
            base = builtins.base
            if hasattr(base, 'sfxManagerList') and base.sfxManagerList:
                base.sfxManagerList[0].setVolume(val / 100.0)
            if hasattr(base, 'musicManager') and base.musicManager:
                base.musicManager.setVolume(val / 100.0)
        except Exception:
            pass

    # ── Input (mode écoute) ───────────────────────────────────────────────────

    def input(self, key):
        if not self.listening_row:
            return
        # Clic gauche : géré par Button.on_click + select_row
        if key == 'left mouse down':
            return
        if key == 'right mouse down':
            self._apply_key('right mouse')
            return
        if key.endswith(' up') or key in ('scroll up', 'scroll down', 'middle mouse down'):
            return
        if key.startswith('gamepad'):
            return
        if key == 'escape':
            self.listening_row.set_listening(False)
            self.listening_row = None
            return
        self._apply_key(key)
