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
            self.y = player.y - player.scale_y/6

        self.collider.visible = player.isDebuging
        hit_info = self.intersects(ignore=[player]+player.team)
        if hit_info.hit:
            entity = hit_info.entity
            if not self.past_state and entity.name != "attack_collider" and (entity.currentAnim != entity.animManager.animations["Defend"][entity.facing] or entity.currentAnim.end) and hit_info.entity.physics.timer == 0:
                player.physics.isThrowing = False
                self.texture = None
                self.model = None
                player.physics.timerShuriken = 0
                hit_info.entity.physics.knockback = (hit_info.entity.position - player.position).normalized() * hit_info.entity.kokoro
                hit_info.entity.physics.knockback[2] = 0
                if (player.facing == "right" and hit_info.entity.physics.knockback[0] < 0) or (player.facing == "left" and hit_info.entity.physics.knockback[0] > 0):
                    hit_info.entity.physics.knockback[0] *= -1
                hit_info.entity.kokoro += 0.5
                player.kokoro_steal += 0.1
                self.past_state = True
                hit_info.entity.animManager.play("Hurt", "play")
            elif (not self.past_state and entity.name != "attack_collider"
                  and "Defend" in entity.animManager.animations
                  and entity.currentAnim == entity.animManager.animations["Defend"][entity.facing]
                  and not entity.currentAnim.end):
                _play_parade()
                self.past_state = True
            if not player.physics.is_attacking :
                self.past_state = False
