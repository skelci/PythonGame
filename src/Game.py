from GameBase import GameBase

from Actor import Actor
from Datatypes import *

class Game(GameBase):
    def begin_play(self):
        self.window_title = "Game"
        self.window_width = 800
        self.window_height = 600

        self.cube = Actor(name = "Cube", half_size = Vector(1, 1), position = Vector(0,0), visible = True, texture = "res/textures/texture.jpeg")

        super().begin_play()

        # Register the actors after the engine has been initialized
        self.engine.register_actor(self.cube)

        self.engine.camera_position = Vector(0, 2)

