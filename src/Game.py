from engine.game_base import GameBase

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.datatypes import *

class Game(GameBase):
    def begin_play(self):
        self.window_title = "Game"
        self.window_width = 800
        self.window_height = 600
        self.fps_cap = 120

        super().begin_play()

        # Register the actors after the engine has been initialized
        reg = lambda actor: self.engine.register_actor(actor)
        # name, half_size, position, visible, texture, initial_velocity
        reg(Actor("Cube", Vector(5, 1), Vector(0, 0), True, "res/textures/texture.jpeg"))
        reg(Actor("Cube2", Vector(1, 3), Vector(-5, 2), True, "res/textures/texture.jpeg"))
        reg(Actor("Cube3", Vector(1, 3), Vector(5, 2), True, "res/textures/texture.jpeg"))
        reg(Rigidbody("Rigidbody", Vector(1, 1), Vector(-2, 2), True, "res/textures/texture.jpeg", Vector(1, 0)))
        reg(Rigidbody("Rigidbody2", Vector(1, 1), Vector(2, 2), True, "res/textures/texture.jpeg", Vector(-1, 0)))

        self.engine.camera_position = Vector(4, 3)
        self.engine.camera_width = 20


    def tick(self):
        delta_time = super().tick()
        # print(1 if not delta_time else 1/delta_time) # Uncomment to print FPS

