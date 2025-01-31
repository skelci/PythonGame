from Engine.GameBase import GameBase

from Components.Actor import Actor
from Components.Datatypes import *

class Game(GameBase):
    def begin_play(self):
        self.window_title = "Game"
        self.window_width = 800
        self.window_height = 600
        self.fps_cap = 120

        self.cube = Actor(name = "Cube", half_size = Vector(1, 1), position = Vector(0,0), visible = True, texture = "res/textures/texture.jpeg")

        super().begin_play()

        # Register the actors after the engine has been initialized
        self.engine.register_actor(self.cube)

        self.engine.camera_position = Vector(0, 2)


    def tick(self):
        delta_time = super().tick()
        # print(1 if not delta_time else 1/delta_time) # Uncomment to print FPS

