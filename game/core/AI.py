from ursina import *
import random
from game.core.variables import Variables

FIGHT_RANGE_X  = 2.5   # distance x pour attaquer
FIGHT_RANGE_Y  = 2.0   # distance y pour attaquer
CEIL_CHECK     = 3.0   # distance raycast plafond
CEIL_BLOCK_MAX = 0.5   # durée max bloqué par plafond
SPAWN_PROTECT  = 2.0   # spawn clean

class AI:
    def __init__(self, player, level=1):
        self.type   = "AI"
        self.player = player
        self.level  = level

        self.inputs = {k: 0 for k in
                       ["left", "right", "up", "dash", "get off",
                        "interact", "defend", "jump", "attack", "play", "throw"]}
        self.old_inputs = self.inputs.copy()

        self.data             = {}
        self.timer            = 0
        self.delay            = {1: 0.5, 2: 0.18, 3: 0.08}.get(level, 0.5)

        self.defend_cooldown  = 0.0
        self.punish_window    = 0.0
        self.ceil_blocked_t   = 0.0
        self.recovering       = False

        self._needs_jump      = False  
        self._fight_recoil_t  = 0.0   
        self._solids          = None   
        self._spawn_timer     = SPAWN_PROTECT  

        self.my_platform      = None
        self.target_platform  = None

    def perceive(self):
        p   = self.player
        phy = p.physics

        self.data["vel_y"]  = phy.velocity_y
        self.data["vel_x"]  = phy.velocity_x
        self.data["jumps"]  = phy.remaining_jump
        self.data["kokoro"] = p.kokoro

        pos    = Vec3(p.x, p.y, -1)
        ignore = [p] + p.team + p.enemy

        self.data["void_c"] = not raycast(pos,                     Vec3(0,-1,0), 5, ignore=ignore).hit
        self.data["void_l"] = not raycast(pos + Vec3(-0.8,-0.5,0), Vec3(0,-1,0), 3, ignore=ignore).hit
        self.data["void_r"] = not raycast(pos + Vec3( 0.8,-0.5,0), Vec3(0,-1,0), 3, ignore=ignore).hit
        self.data["safe"]   = not self.data["void_c"]

        # Plafond : on ne compte que les "solid", pas les plateformes traversables
        ceil_hit          = raycast(pos, Vec3(0, 1, 0), CEIL_CHECK, ignore=ignore)
        self.data["ceil"] = ceil_hit.hit and getattr(ceil_hit.entity, "name", "") == "solid"

        hit_below        = raycast(pos, Vec3(0,-1,0), 2, ignore=ignore)
        self.my_platform = hit_below.entity if hit_below.hit else None

        target = self.player.enemy[0] if self.player.enemy else None
        if target is not None:
            t = target
            self.data["dx"] = t.x - p.x
            self.data["dy"] = t.y - p.y
            self.data["target_kokoro"] = t.kokoro
            self.data["target_vel_x"]  = t.physics.velocity_x
            self.data["target_vel_y"]  = t.physics.velocity_y
            self.data["target_safe"]   = not self.is_over_void(t)

            if self.level == 3 and not self.data["target_safe"]:
                pred_x, pred_y = self.predict_landing(t)
                hit_t = raycast(Vec3(pred_x, pred_y, -1), Vec3(0,-1,0), 3, ignore=ignore)
            else:
                hit_t = raycast(t.position, Vec3(0,-1,0), 3, ignore=ignore)
            self.target_platform = hit_t.entity if hit_t.hit else None

            self.data["target_attacking"]  = t.physics.is_attacking
            self.data["target_defending"]  = (t.currentAnim == t.animManager.animations["Defend"][t.facing])
            self.data["target_defend_end"] = (self.data["target_defending"] and t.currentAnim.end)
            self.data["target_over_void"]  = not self.data["target_safe"]
        else:
            self.data["dx"]                = 0
            self.data["dy"]                = 0
            self.data["target_kokoro"]     = 1
            self.data["target_vel_x"]      = 0
            self.data["target_vel_y"]      = 0
            self.data["target_safe"]       = True
            self.data["target_over_void"]  = False
            self.data["target_attacking"]  = False
            self.data["target_defending"]  = False
            self.data["target_defend_end"] = False
            self.target_platform           = None

    def empty(self):
        return {k: 0 for k in self.inputs}

    def is_over_void(self, entity):
        origin = Vec3(entity.x, entity.y, -1)
        return not raycast(origin, Vec3(0, -1, 0), 8, ignore=[entity]).hit

    def predict_landing(self, target):
        """Prédit la position d'atterrissage de la cible (N3 uniquement)."""
        vel_y = target.physics.velocity_y
        if vel_y >= 0:
            return target.x, target.y
        t_land = abs(vel_y) / Variables.GRAVITY
        return target.x + target.physics.velocity_x * t_land, target.y + vel_y * t_land

    def nearest_solid(self):
        """Retourne la plateforme solid la plus proche.
        La liste est mise en cache à la première utilisation car les plateformes sont statiques."""
        if self._solids is None:
            self._solids = [e for e in scene.entities if getattr(e, "name", "") == "solid"]
        best      = None
        best_dist = float("inf")
        for e in self._solids:
            dist = abs(e.x - self.player.x) + abs(e.y - self.player.y)
            if dist < best_dist:
                best_dist = dist
                best      = e
        return best

    def is_danger(self):
        """Chute imminente — priorité absolue. Ignoré pendant le spawn."""
        if self._spawn_timer > 0:
            return False
        if self.level == 1:
            return self.data["void_c"]
        return self.data["void_c"] and self.data["vel_y"] < 0

    def recover(self):
        """
        Revenir sur une plateforme.
        - Coupe get off immédiatement (résidu de chase)
        - Vérifie le plafond avant de sauter
        - Va vers la plateforme solid la plus proche
        """
        self.recovering       = True
        intentions            = self.empty()
        intentions["get off"] = 0

        vel_y = self.data["vel_y"]
        jumps = self.data["jumps"]

        solid = self.nearest_solid()
        if solid:
            dx_to = solid.x - self.player.x
            if dx_to > 0.3:
                intentions["right"] = 2
            elif dx_to < -0.3:
                intentions["left"] = 2

        if vel_y < -1 and jumps > 0:
            if not self.data["ceil"]:
                self._needs_jump = True
            else:
                self.ceil_blocked_t += time.dt
                if self.ceil_blocked_t > CEIL_BLOCK_MAX:
                    self._needs_jump    = True
                    self.ceil_blocked_t = 0
        else:
            self.ceil_blocked_t = 0

        return intentions

    def flee(self):
        """N2 uniquement — fuir dans la direction opposée à la cible."""
        intentions = self.empty()
        dx = self.data["dx"]

        if dx > 0:
            if not self.data["void_l"]:
                intentions["left"] = 2
            else:
                intentions["right"] = 2
        else:
            if not self.data["void_r"]:
                intentions["right"] = 2
            else:
                intentions["left"] = 2

        return intentions

    def chase(self):
        """
        Se déplacer vers la plateforme de la cible.
          - Cible en dessous (dy < -2) : get off hold + avancer en x
          - Cible au-dessus (dy > 2)   : avancer en x + sauter
          - Même niveau                : approche directe
        """
        intentions = self.empty()
        dx    = self.data["dx"]
        dy    = self.data["dy"]
        jumps = self.data["jumps"]

        # Cible en dessous
        if dy < -2:
            intentions["get off"] = 2
            if dx > 0.4:
                intentions["right"] = 2
                if self.level >= 2 and abs(dx) > 5:
                    intentions["dash"] = 1
            elif dx < -0.4:
                intentions["left"] = 2
                if self.level >= 2 and abs(dx) > 5:
                    intentions["dash"] = 1

        # Cible au-dessus
        elif dy > 2:
            intentions["get off"] = 0
            if dx > 0.4:
                intentions["right"] = 2
            elif dx < -0.4:
                intentions["left"] = 2

            if jumps > 0 and not self.data["ceil"]:
                intentions["jump"] = 1
            elif jumps > 0:
                self.ceil_blocked_t += time.dt
                if self.ceil_blocked_t > CEIL_BLOCK_MAX:
                    intentions["jump"]  = 1
                    self.ceil_blocked_t = 0

        # Même niveau
        else:
            intentions["get off"] = 0
            if dx > 0.4:
                intentions["right"] = 2
                if self.level >= 2 and abs(dx) > 5:
                    intentions["dash"] = 1
            elif dx < -0.4:
                intentions["left"] = 2
                if self.level >= 2 and abs(dx) > 5:
                    intentions["dash"] = 1

        return intentions

    def fight(self):
        """
        Attaque ou défend quand la cible est à portée.
        Retourne un dict d'intentions (peut se combiner avec chase).
        """
        intentions    = self.empty()
        dx            = self.data["dx"]
        dy            = self.data["dy"]
        target_void   = self.data["target_over_void"]
        target_kokoro = self.data["target_kokoro"]

        # Défense
        if (self.data["target_attacking"]
                and abs(dx) < FIGHT_RANGE_X
                and abs(dy) < FIGHT_RANGE_Y
                and self.data["safe"]):
            if self.level == 3 and self.defend_cooldown <= 0:
                self.defend_cooldown = random.uniform(0.4, 0.7)
                self.punish_window   = 0.4
                intentions["defend"] = 1
                return intentions
            elif self.level == 2 and self.defend_cooldown <= 0 and random.random() < 0.55:
                self.defend_cooldown = 1.2
                intentions["defend"] = 1
                return intentions

        # Punition N3
        if self.level == 3 and self.punish_window > 0 and abs(dx) < FIGHT_RANGE_X:
            intentions["attack"] = 1
            return intentions

        # Recul tactique si trop près (N2/N3) 
        if abs(dx) < 1.2 and self.data["safe"] and self.level >= 2 and self._fight_recoil_t <= 0:
            if dx > 0 and not self.data["void_l"]:
                intentions["left"]   = 2
                self._fight_recoil_t = 0.3
            elif dx < 0 and not self.data["void_r"]:
                intentions["right"]  = 2
                self._fight_recoil_t = 0.3

        # Attaque
        if abs(dx) < FIGHT_RANGE_X and abs(dy) < FIGHT_RANGE_Y:
            if self.level == 1:
                intentions["attack"] = 1

            elif self.level == 2:
                intentions["attack"] = 1

            elif self.level == 3:
                if not self.data["safe"]:
                    # Dans le vide : attaque directe
                    intentions["attack"] = 1
                elif target_kokoro >= 2.5 and target_void:
                    # Cible fragilisée dans le vide : up+attack pour éjecter
                    intentions["up"]     = 2
                    intentions["attack"] = 1
                elif self.data["target_defend_end"]:
                    # Fin de défense adverse : punir immédiatement
                    intentions["attack"] = 1
                else:
                    intentions["attack"] = 1

        return intentions

    def control(self):
        """
        Cible dans le vide : se repositionner avantageusement.
        N1/N2 : attendre au bord côté cible
        N3    : edgeguard actif
        """
        intentions = self.empty()
        dx = self.data["dx"]

        if dx > 0 and not self.data["void_r"]:
            intentions["right"] = 2
        elif dx < 0 and not self.data["void_l"]:
            intentions["left"] = 2

        return intentions

    def apply_inputs(self, intentions):
        for k in self.inputs:
            want = intentions.get(k, 0)
            if want > 0:
                if k == "jump":
                    self.inputs[k] = 1 if self.old_inputs[k] == 0 else 0
                else:
                    self.inputs[k] = 1 if self.old_inputs[k] == 0 else 2
            else:
                self.inputs[k] = 0

        if self._needs_jump:
            if self.inputs["jump"] == 0:
                self.old_inputs["jump"] = 0
            else:
                self._needs_jump = False

        self.old_inputs = self.inputs.copy()

    def update(self):
        self.perceive()

        self.defend_cooldown  = max(0.0, self.defend_cooldown  - time.dt)
        self.punish_window    = max(0.0, self.punish_window    - time.dt)
        self._fight_recoil_t  = max(0.0, self._fight_recoil_t - time.dt)
        self._spawn_timer     = max(0.0, self._spawn_timer     - time.dt)

        # Priorité absolue : RECOVER (désactivé pendant le spawn)
        if self.is_danger():
            self.apply_inputs(self.recover())
            self.timer = 0
            self.player.inputManager.inputs = self.inputs
            return

        # Recover terminé
        if self.recovering and self.data["safe"]:
            self.recovering     = False
            self.ceil_blocked_t = 0
            self._needs_jump    = False

        # Timer
        self.timer += time.dt
        if self.timer < self.delay:
            self.player.inputManager.inputs = self.inputs
            return
        self.timer = 0

        final = self.empty()

        # Flee (N2 N3, HP critique)
        if (self.level == 2 or self.level == 3) and self.player.hp <= 1 and self.player.kokoro >= 2.0:
            if random.random() < 0.35:
                self.apply_inputs(self.flee())
                self.player.inputManager.inputs = self.inputs
                return

        dx = self.data["dx"]
        dy = self.data["dy"]
        in_fight_range = abs(dx) < FIGHT_RANGE_X and abs(dy) < FIGHT_RANGE_Y

        # Décision principale
        if self.data["target_over_void"]:
            final.update({k: v for k, v in self.control().items() if v != 0})

        elif in_fight_range:
            final.update({k: v for k, v in self.fight().items() if v != 0})

        else:
            chase_i = self.chase()
            fight_i = self.fight()
            final.update({k: v for k, v in chase_i.items() if v != 0})
            for k, v in fight_i.items():
                if v != 0 and final.get(k, 0) == 0:
                    final[k] = v

        self.apply_inputs(final)
        self.player.inputManager.inputs = self.inputs