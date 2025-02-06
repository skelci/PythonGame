from engine.game_base import GameBase

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.datatypes import *
from components.material import Material
from components.character import Character
from components.widget import Widget



class Game(GameBase):
    def begin_play(self):
        self.window_title = "Game"
        self.window_width = 1200
        self.window_height = 800
        self.windowed = True
        self.fps_cap = 300
        self.min_tps = 100

        grass = Material("res/textures/texture.jpeg")

        idk = Widget("idk", Vector(100, 100), Vector(100, 100), 0, color=Color(192, 31, 215))

        super().begin_play()

        # Register actors & widgets after engine has been initialized
        eng = self.engine
        reg = lambda actor: eng.register_actor(actor)
        regw = lambda widget: eng.register_widget(widget)

        #   class     name,         half_size,        position,        visible, material, restitution, inital_velocity, min_velocity, mass, gravity_scale, friction, air_resistance
        reg(Actor    ("Cube1"     , Vector(10 , 0.5), Vector( 0 ,  5), True, grass, 1))
        reg(Actor    ("Cube2"     , Vector(0.5, 5  ), Vector( 10,  0), True, grass, 1))
        reg(Actor    ("Cube3"     , Vector(10 , 0.5), Vector( 0 , -5), True, grass, 1))
        reg(Actor    ("Cube4"     , Vector(0.5, 5  ), Vector(-10,  0), True, grass, 1))
        reg(Rigidbody("Rigidbody1", Vector(0.5, 0.5), Vector( 2 ,  2), True, grass, 0.9, Vector(6, 7), 0, 8 , 1, 0.1, 0.01))
        reg(Rigidbody("Rigidbody2", Vector(0.5, 0.5), Vector( 2 , -2), True, grass, 0.9, Vector(7, 6), 0, 4 , 1, 0.1, 0.01))
        reg(Rigidbody("Rigidbody3", Vector(0.5, 0.5), Vector(-3 ,  2), True, grass, 0.9, Vector(4, 9), 0, 1 , 1, 0.1, 0.01))
        reg(Rigidbody("Rigidbody4", Vector(0.5, 0.5), Vector(-3 , -2), True, grass, 0.9, Vector(9, 4), 0, 96, 1, 0.1, 0.01))
        reg(Character("Character" , Vector(0.5, 1), material=grass))

        regw(idk)

        eng.camera_position = Vector(0, 0)
        eng.camera_width = 20

        eng.widgets["idk"].visible = True


    def tick(self):
        delta_time = super().tick()
        if not self.engine.running:
            return
        # print(1 if not delta_time else 1/delta_time) # Uncomment to print FPS

