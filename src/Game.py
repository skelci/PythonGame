from engine.game_base import GameBase

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.datatypes import *



class Game(GameBase):
    def begin_play(self):
        self.window_title = "Game"
        self.window_width = 1200
        self.window_height = 800
        self.windowed = True
        self.fps_cap = 300
        self.min_tps = 100

        super().begin_play()

        # Register actors after engine has been initialized
        eng = self.engine
        reg = lambda actor: eng.register_actor(actor)
        #   class     name,         half_size,        position,        visible, texture,                  restitution, inital_velocity, min_velocity, mass, gravity_scale, friction, air_resistance
        reg(Actor    ("Cube1"     , Vector(10 , 0.5), Vector( 0 ,  5), True, "res/textures/texture.jpeg", 1))
        reg(Actor    ("Cube2"     , Vector(0.5, 5  ), Vector( 10,  0), True, "res/textures/texture.jpeg", 1))
        reg(Actor    ("Cube3"     , Vector(10 , 0.5), Vector( 0 , -5), True, "res/textures/texture.jpeg", 1))
        reg(Actor    ("Cube4"     , Vector(0.5, 5  ), Vector(-10,  0), True, "res/textures/texture.jpeg", 1))
        reg(Rigidbody("Rigidbody1", Vector(0.5, 0.5), Vector( 2 ,  2), True, "res/textures/texture.jpeg", 0.9, Vector(6, 7), 0, 8 , 1, 0.1, 0.01))
        reg(Rigidbody("Rigidbody2", Vector(0.5, 0.5), Vector( 2 , -2), True, "res/textures/texture.jpeg", 0.9, Vector(7, 6), 0, 4 , 1, 0.1, 0.01))
        reg(Rigidbody("Rigidbody3", Vector(0.5, 0.5), Vector(-3 ,  2), True, "res/textures/texture.jpeg", 0.9, Vector(4, 9), 0, 1 , 1, 0.1, 0.01))
        reg(Rigidbody("Rigidbody4", Vector(0.5, 0.5), Vector(-3 , -2), True, "res/textures/texture.jpeg", 0.9, Vector(9, 4), 0, 96, 1, 0.1, 0.01))

        eng.camera_position = Vector(0, 0)
        eng.camera_width = 20


    def tick(self):
        delta_time = super().tick()
        if not self.engine.running:
            return
        # print(1 if not delta_time else 1/delta_time) # Uncomment to print FPS

