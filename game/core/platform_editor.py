from ursina import *
import keyboard as kb


class PlatformEditor(Entity):
    """
    Editeur de plateformes en temps réel (map2 / map3).

    Clic gauche        → sélectionner un bloc
    Flèches            → déplacer  (Shift = ×5)
    Ctrl + Flèches     → redimensionner  (Shift = ×5)
    Entrée             → arrondir pos à 0.05, taille à 0.1
    Échap / clic vide  → désélectionner
    """

    _MOV_SPD  = 1.2   # unités / s  (déplacement lent)
    _MOV_FAST = 6.0   # unités / s  (Shift)
    _RSZ_SPD  = 0.6   # unités / s  (redimension lente)
    _RSZ_FAST = 3.0   # unités / s  (Shift)

    def __init__(self, platforms):
        super().__init__()
        self.editable    = [p for p in platforms if p.visible]
        self.selected    = None
        self._orig_color = None

        # Panneau d'info (fond semi-transparent + texte)
        self._bg = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(0, 0, 0, 185),
            scale=(0.42, 0.31),
            position=(-0.555, 0.345),
            z=0.3,
        )
        self._info = Text(
            parent=camera.ui,
            position=(-0.755, 0.495),
            scale=1.22,
            color=color.yellow,
            origin=(-0.5, 0.5),
            z=-1,
        )
        self._update_info()

    # ── Sélection ────────────────────────────────────────────────────────────

    def input(self, key):
        if key == 'left mouse down':
            hit = mouse.hovered_entity
            if hit in self.editable:
                self._select(hit)
            else:
                self._deselect()
            return

        if key == 'escape' and self.selected:
            self._deselect()
            return

        # Arrondir les valeurs (Entrée)
        if key == 'enter' and self.selected:
            p = self.selected
            p.x       = round(p.x       / 0.05) * 0.05
            p.y       = round(p.y       / 0.05) * 0.05
            p.scale_x = round(p.scale_x / 0.1 ) * 0.1
            p.scale_y = round(p.scale_y / 0.1 ) * 0.1
            self._update_info()

    def _select(self, p):
        if self.selected and self.selected is not p:
            self.selected.color = self._orig_color
        self.selected    = p
        self._orig_color = p.color
        p.color          = color.yellow
        self._update_info()

    def _deselect(self):
        if self.selected:
            self.selected.color = self._orig_color
            self._orig_color    = None
        self.selected = None
        self._update_info()

    # ── Mouvement & resize (frame par frame) ─────────────────────────────────

    def update(self):
        if not self.selected:
            return

        ctrl  = kb.is_pressed('ctrl')  or kb.is_pressed('left ctrl')  or kb.is_pressed('right ctrl')
        shift = kb.is_pressed('shift') or kb.is_pressed('left shift') or kb.is_pressed('right shift')

        moved  = False
        resized = False

        if not ctrl:
            # ── Déplacement ──
            spd = self._MOV_FAST if shift else self._MOV_SPD
            if kb.is_pressed('left'):  self.selected.x -= spd * time.dt; moved = True
            if kb.is_pressed('right'): self.selected.x += spd * time.dt; moved = True
            if kb.is_pressed('up'):    self.selected.y += spd * time.dt; moved = True
            if kb.is_pressed('down'):  self.selected.y -= spd * time.dt; moved = True
        else:
            # ── Redimensionnement ──
            rs = self._RSZ_FAST if shift else self._RSZ_SPD
            if kb.is_pressed('left'):
                self.selected.scale_x = max(0.2, self.selected.scale_x - rs * time.dt)
                resized = True
            if kb.is_pressed('right'):
                self.selected.scale_x += rs * time.dt
                resized = True
            if kb.is_pressed('up'):
                self.selected.scale_y += rs * time.dt
                resized = True
            if kb.is_pressed('down'):
                self.selected.scale_y = max(0.2, self.selected.scale_y - rs * time.dt)
                resized = True

        if resized:
            # Recréer le collider pour que la collision suive la taille
            try:
                self.selected.collider = BoxCollider(
                    self.selected,
                    size=Vec3(self.selected.scale_x, self.selected.scale_y, 1),
                    center=(0, 0, 0),
                )
            except Exception:
                try:
                    self.selected.collider = 'box'
                except Exception:
                    pass

        if moved or resized:
            self._update_info()

    # ── Affichage ─────────────────────────────────────────────────────────────

    def _update_info(self):
        if not self.selected:
            self._info.text = (
                "  Editeur plateformes\n"
                "  [Clic] selectionner\n"
                "  Fleches  : deplacer\n"
                "  Ctrl+Fl  : redim.\n"
                "  Shift    : x5 vitesse\n"
                "  Entree   : arrondir\n"
                "  Echap    : deselect."
            )
        else:
            p     = self.selected
            label = f"[{p.name}]"
            self._info.text = (
                f"  {label}\n"
                f"  X    : {p.x:.3f}\n"
                f"  Y    : {p.y:.3f}\n"
                f"  Larg : {p.scale_x:.3f}\n"
                f"  Haut : {p.scale_y:.3f}\n"
                f"  ---\n"
                f"  Fleches  : deplacer\n"
                f"  Ctrl+Fl  : redim.\n"
                f"  Shift x5 | Entree arrondir"
            )
