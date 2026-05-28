from ursina import *
from game.core.variables import Variables
from game.manager.resource import resourceManager

Shuriken = resourceManager.picture("shuriken")
_parade_sound = None

def _play_parade():
    global _parade_sound
    if _parade_sound is None:
        try:
            _parade_sound = Audio('game/resources/sounds/music/parade.wav', autoplay=False, loop=False)
        except Exception:
            _parade_sound = False
    if _parade_sound:
        try:
            _parade_sound.play()
        except Exception:
            pass

class Attack(Entity):
    def __init__(self, scale, position, player, **kwargs):
        super().__init__(
            model=None,
            name="attack_collider",
            texture=None,
            **kwargs
        )
        self.scale_x = scale[0]
        self.scale_y = scale[1]
        self.x = position[0]
        self.y = position[1]
        self.player = player
        self.collider = BoxCollider(self, size=Vec3(self.scale[0], self.scale[1], 1), center=(0, 0, 0))
        self.collider.visible = self.player.isDebuging
        self.collider.color = color.rgba(100, 100, 50, 120)
        self.past_state = False
        if self.player.physics.isThrowing:
            self.model = "quad"
            self.texture = Shuriken
        self.facing = self.player.facing

    def update(self):
        player = self.player
        if player.physics.isThrowing :
            if self.facing == "right":
                self.x += Variables.PLAYER_SPEED * 2 * time.dt
                self.rotation_z += 50
            else:
                self.x -= Variables.PLAYER_SPEED * 2 * time.dt
                self.rotation_z -= 50
        else:
            self.y = player.y - player.scale_y / 6

        self.collider.visible = player.isDebuging

        # On ignore aussi les ennemis réseau (network_controlled) pour la détection
        # de collision — ils ne sont que visuels, le vrai joueur est sur l'autre machine
        ignore_list = [player] + player.team
        for e in player.enemy:
            if hasattr(e, 'inputManager') and e.inputManager.network_controlled:
                ignore_list.append(e)

        hit_info = self.intersects(ignore=ignore_list)
        if hit_info.hit:
            entity = hit_info.entity
            if (not self.past_state
                    and entity.name != "attack_collider"
                    and (entity.currentAnim != entity.animManager.animations["Defend"][entity.facing] or entity.currentAnim.end)
                    and entity.physics.timer == 0):

                player.physics.isThrowing = False
                self.texture = None
                self.model = None
                player.physics.timerShuriken = 0

                kb = (entity.position - player.position).normalized() * entity.kokoro
                kb[2] = 0
                if (player.facing == "right" and kb[0] < 0) or (player.facing == "left" and kb[0] > 0):
                    kb[0] *= -1

                # Appliquer localement (PNJ ou coop locale)
                entity.physics.knockback = kb
                entity.kokoro += 0.5
                player.kokoro_steal += 0.1
                self.past_state = True
                entity.animManager.play("Hurt", "play")

                # Envoyer le knockback à la machine adverse via le réseau
                net = getattr(player, 'net', None)
                if net:
                    net.send("server_hit", {
                        "knockback_x": kb[0],
                        "knockback_y": kb[1],
                        "kokoro":      entity.kokoro,
                    })

            if not player.physics.is_attacking:
                self.past_state = False
