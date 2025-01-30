from GameBase import GameBase

from Cube import Cube
from Datatypes import *


class Game(GameBase):
    def begin_play(self):
        self.window_title = "Game"
        self.window_width = 800
        self.window_height = 600

        cube = Cube("Cube", 1, 1, 1, "res/textures/texture.jpeg")

        super().begin_play()

        # Register the actors after the engine has been initialized
        self.engine.register_actor(cube)

        self.engine.renderer.camera.position = Vector(0, 0, 2)
        self.engine.renderer.camera.rotation = Rotator().set_degrees(-90, 0, 0)


    def tick(self):
        super().tick()

        print("Tick")
    
