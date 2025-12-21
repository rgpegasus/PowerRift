# Pour des petites fonctions réutilisées souvent
from ursina import *
from game.manager.resource import resourceManager
class Animation:
    def __init__(self, entity, texture, nbf, fps=10, direction = 1):
        self.entity = entity
        self.texture = texture
        self.number_frames = nbf
        self.fps = fps
        self.frame_index = 0
        self.timer = 0
        self.entity.texture_offset = (0 / self.number_frames, 0)
        self.is_playing_once = False  
        self.end = False
        self.direction = direction
        if self.direction == 1:
            self.facing = "right"
        else:
            self.facing = "left"

    def loop(self):
        self.entity.texture_scale = (self.direction/self.number_frames, 1)
        self.frame_index = 0
        self.entity.texture = self.texture
        self.texture_offset = (0 / self.number_frames, 0)
        self.timer = 0
        self.is_playing_once = False 

    def play(self):
        self.entity.texture_scale = (self.direction/self.number_frames, 1)
        self.frame_index = 0
        self.texture_offset = (0 / self.number_frames, 0)
        self.entity.texture = self.texture
        self.timer = 0
        self.is_playing_once = True 
        self.end = False 

    def update(self):
        self.timer += time.dt
        if self.timer >= 1/self.fps:
            self.timer = 0
            if self.entity.facing != self.facing:
                self.facing = self.entity.facing
                self.direction*=-1
                self.entity.texture_scale = (self.direction/self.number_frames, 1)
            if self.is_playing_once:
                if self.frame_index < self.number_frames - 1:
                    self.frame_index += 1
                else:
                    self.end = True
                    return
            else:
                self.frame_index = (self.frame_index + 1) % self.number_frames


            self.entity.texture_offset = (self.frame_index / self.number_frames, 0)

smoke = resourceManager.picture("smoke")
class JumpSmoke(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(
            model="quad", 
            texture= smoke,
            z=-1,
            **kwargs
        )
        self.visible = False
        self.scale=1
        self.player = player
        self.facing = "right"
        self.animSmoke = Animation(self, smoke, 10)

    def isJumping(self, direction = "down", max = False):
        self.visible = True
        if max:
            self.color = color.red
        else:
            self.color = color.white
        player_scale_x = self.player.scale_x*self.player.scale_val[0]/2
        player_scale_y = self.player.scale_y*self.player.scale_val[1]/2 - self.player.collider.center[1] * self.player.scale_y
        if direction == "down":
            self.position = (self.player.x, self.player.y - player_scale_y + self.scale_y/2)
            self.rotation = (0,0,0)
        elif direction == "left":
            self.position = (self.player.x + player_scale_x - self.scale_y/2 , self.player.y - player_scale_y + self.scale_y/2)
            self.rotation = (0,0,-90)
        elif direction == "right":
            self.position = (self.player.x - player_scale_x + self.scale_y/2 , self.player.y - player_scale_y + self.scale_y/2)
            self.rotation = (0,0,90)

        self.animSmoke.play()
    def update(self):
        self.animSmoke.update() 
      