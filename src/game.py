from engine.game_base import GameBase

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.datatypes import *
from components.material import Material
from components.character import Character
from components.button import Button



# class Game(GameBase):
#     def begin_play(self):
#         super().begin_play()

#         grass = Material("res/textures/grass.jpeg")

#         self.engine.title = "Game"
#         self.engine.width = 1200
#         self.engine.height = 800
#         self.engine.windowed = True
#         self.engine.tps = 100
#         self.engine.fps = 100

#         # Register actors & widgets after engine has been initialized
#         eng = self.engine
#         reg = lambda actor: eng.register_actor(actor)
#         regw = lambda widget: eng.register_widget(widget)

#         #   class     self, name,         half_size,        position,        visible, material, restitution, inital_velocity, min_velocity, mass, gravity_scale, friction, air_resistance
#         reg(Actor    (self, "Cube1"     , Vector(10 , 0.5), Vector( 0 ,  5), False, True, True, grass, 1))
#         reg(Actor    (self, "Cube2"     , Vector(0.5, 5  ), Vector( 10,  0), False, True, True, grass, 1))
#         reg(Actor    (self, "Cube3"     , Vector(10 , 0.5), Vector( 0 , -5), False, True, True, grass, 1))
#         reg(Actor    (self, "Cube4"     , Vector(0.5, 5  ), Vector(-10,  0), False, True, True, grass, 1))
#         reg(Rigidbody(self, "Rigidbody1", Vector(0.5, 0.5), Vector( 2 ,  2), False, True, True, True, grass, 0.9, Vector(6, 7), 0, 8 , 1, 0.1, 0.01))
#         reg(Rigidbody(self, "Rigidbody2", Vector(0.5, 0.5), Vector( 2 , -2), False, True, True, True, grass, 0.9, Vector(7, 6), 0, 4 , 1, 0.1, 0.01))
#         reg(Rigidbody(self, "Rigidbody3", Vector(0.5, 0.5), Vector(-3 ,  2), False, True, True, True, grass, 0.9, Vector(4, 9), 0, 1 , 1, 0.1, 0.01))
#         reg(Rigidbody(self, "Rigidbody4", Vector(0.5, 0.5), Vector(-3 , -2), False, True, True, True, grass, 0.9, Vector(9, 4), 0, 96, 1, 0.1, 0.01))
#         reg(Character(self, "Character" , Vector(0.5, 1), material=grass, gravity_scale=1))

#         regw(Button("idk", Vector(100, 100), Vector(200, 50), 0, border_color=Color(192, 31, 215), bg_color=Color(31, 2, 19), font="res/fonts/arial.ttf", text_color=Color(192, 31, 215), text="I don't know", font_size=20, thickness=5, action = lambda: print("I don't know"), hover_color=Color(60, 10, 80), click_color=Color(3, 10, 5)))

#         eng.camera_position = Vector(0, 0)
#         eng.camera_width = 20

#         eng.widgets["idk"].visible = True


#     def tick(self):
#         delta_time = super().tick()
#         if not self.engine.running:
#             return
        
#         if Key.SPACE in self.engine.pressed_keys:
#             self.engine.actors["Character"].jump()
#         if Key.A in self.engine.pressed_keys:
#             self.engine.actors["Character"].move_direction = -1
#         elif Key.D in self.engine.pressed_keys:
#             self.engine.actors["Character"].move_direction = 1
#         else:
#             self.engine.actors["Character"].move_direction = 0

import random as r
from components.text import Text



class Player(Character):
    def jump(self):
        self.velocity.y = self.jump_velocity


    def on_collision(self, collision_data):
        super().on_collision(collision_data)

        self.game_ref.die()


    def tick(self, delta_time):
        super().tick(delta_time)

        if not -10 < self.position.y < 10:
            self.game_ref.die()



class Pipe(Actor):
    def tick(self, delta_time):
        super().tick(delta_time)

        self.position.x -= 3 * delta_time

        if self.position.x < -15:
            self.game_ref.engine.destroy_actor(self.name)



class ScoreUpdater(Actor):
    def tick(self, delta_time):
        super().tick(delta_time)

        self.position.x -= 3 * delta_time

        if self.position.x < -15:
            self.game_ref.engine.destroy_actor(self.name)


    def on_overlap_begin(self, other_actor):
        super().on_collision(other_actor)
        if other_actor.name != "Player":
            return

        self.game_ref.score += 1
        self.game_ref.engine.widgets["score"].text = f"Score: {self.game_ref.score}"
        self.game_ref.engine.destroy_actor(self.name)



class Game(GameBase):
    def begin_play(self):
        super().begin_play()

        self.engine.title = "Birdie"

        bird_mat = Material("res/textures/birdie.png")
        self.pipe_mat = Material("res/textures/green.jpeg")

        eng = self.engine
        reg = lambda actor: eng.register_actor(actor)
        regw = lambda widget: eng.register_widget(widget)

        regw(Text("dead", Vector(0, 0), Vector(1600, 900), 1, "res/fonts/arial.ttf", Color(0, 0, 0, 100), False, "You died", Color(255,0,0), 100, Alignment.CENTER))
        regw(Text("score", Vector(700, 10), Vector(200, 40), 2, "res/fonts/arial.ttf", Color(0, 0, 0, 100), True, "Score: 0", Color(255, 255, 255), 32, Alignment.CENTER))

        reg(Player(self, "Player" , Vector(0.25, 0.25), Vector(-7, 3), material=bird_mat, gravity_scale=1.5, jump_velocity=6))

        eng.camera_position = Vector(0, 0)
        eng.camera_width = 20

        eng.widgets["fps"].visible = True

        self.index = 0
        self.dead = False
        self.score = 0

        self.clock = 0


    def die(self):
        self.engine.widgets["dead"].visible = True
        self.dead = True
        self.engine.simulation_speed = 0


    def tick(self):
        delta_time = super().tick()
        if self.dead:
            return
        if not self.engine.running:
            return
        
        reg = lambda actor: self.engine.register_actor(actor)

        if Key.SPACE in self.engine.released_keys:
            self.engine.actors["Player"].jump()

        self.clock += delta_time

        if self.clock > 1.5:
            offset = r.randrange(-2, 2)
            self.clock = 0
            self.index += 1
            self.engine.simulation_speed += 0.005
            reg(Pipe(self,"Pipe_t_" + str(self.index), Vector(0.5, 10), Vector(12, offset + 12), False, True, True, self.pipe_mat))
            reg(Pipe(self,"Pipe_b_" + str(self.index), Vector(0.5, 10), Vector(12, offset - 12), False, True, True, self.pipe_mat))
            reg(ScoreUpdater(self, "ScoreUpdater_" + str(self.index), Vector(0.5, 10), Vector(12, 0), False, False, False))


        
