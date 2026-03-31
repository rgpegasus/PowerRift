from ursina import *
   
class Attack(Entity):
    def __init__(self, scale, position, player, **kwargs):
        super().__init__(
            name="attack_collider",
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
        
    def update(self):
        self.collider.visible = self.player.isDebuging
        hit_info = self.intersects(ignore=[self.player])
        if hit_info.hit:
            entity = hit_info.entity

            if not self.past_state and entity.name != "attack_collider" and (entity.currentAnim != entity.animManager.animations["Defend"][entity.facing] or entity.currentAnim.end):
                hit_info.entity.timer = 0
                hit_info.entity.physics.knockback = (hit_info.entity.position - self.player.position).normalized() * hit_info.entity.kokoro
                hit_info.entity.physics.knockback[2] = 0
                hit_info.entity.kokoro += 0.5
                self.past_state = True
                hit_info.entity.animManager.play("Hurt", "play")
            if not self.player.physics.is_attacking :
                self.past_state = False
                
        

        
    