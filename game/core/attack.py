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
        self.collider.visible = False
        self.collider.color = color.rgba(100, 100, 50, 120)
        self.past_state = False
        
    def update(self):
        hit_info = self.intersects(ignore=[self.player])
        if hit_info.hit:
            entity = hit_info.entity

            if not self.past_state and (entity.currentAnim != entity.animManager.animations["Defend"][entity.facing] or player.currentAnim.end):
                new_hp = hit_info.entity.hp - 10
                hit_info.entity.hp = max(0, new_hp)
                self.past_state = True
                if hit_info.entity.hp == 0:
                    hit_info.entity.animManager.play("Death", "play")
                    hit_info.entity.hp_ui.text = ""
                else:
                    hit_info.entity.animManager.play("Hurt", "play")
            if not self.player.physics.is_attacking :
                self.past_state = False
                
        

        
    