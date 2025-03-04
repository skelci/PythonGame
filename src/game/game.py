from engine.game_base import *

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.datatypes import *
from components.material import Material
from components.character import Character
from components.button import Button
from components.background import *
from components.text import Text

import random as r



#?ifdef CLIENT
class ClientGame(ClientGameBase):
    pass

#?endif



#?ifdef SERVER
class ServerGame(ServerGameBase):
    def __init__(self):
        super().__init__()

        self.engine.console.handle_cmd("build_server")
        self.engine.console.handle_cmd("build_client")

        self.engine.max_tps = 300

        self.engine.start_network("0.0.0.0", 5555, 10)

#?endif



# All games below need a serious refactor. They were made before adding multiplayer support and are not compatible with it.

# Below is a simple physics simulation, uncomment to run it -------------------



# class Game(GameBase):
#     def begin_play(self):
#         super().begin_play()

#         grass = Material("res/textures/grass.jpeg")

#         self.engine.title = "Game"
#         self.engine.width = 1200
#         self.engine.height = 800
#         self.engine.windowed = True
#         self.engine.tps = 30
#         self.engine.fps = 240

#         # Register actors & widgets after engine has been initialized
#         eng = self.engine
#         reg = lambda actor: eng.register_actor(actor)
#         regw = lambda widget: eng.register_widget(widget)

#         reg(Actor    (self, "Cube1"     , Vector(10 , 0.5), Vector( 0 ,  5), False, True, True, grass, 1))
#         reg(Actor    (self, "Cube2"     , Vector(0.5, 5  ), Vector( 10,  0), False, True, True, grass, 1))
#         reg(Actor    (self, "Cube3"     , Vector(10 , 0.5), Vector( 0 , -5), False, True, True, grass, 1))
#         reg(Actor    (self, "Cube4"     , Vector(0.5, 5  ), Vector(-10,  0), False, True, True, grass, 1))
#         reg(Character(self, "Character" , Vector(0.5, 1), material=grass, gravity_scale=1))

#         for i in range(20):
#             reg(Rigidbody(self, "Rigidbody_" + str(i), Vector(0.25, 0.25), Vector(i%10 - 5, i//10 - 3), False, True, True, True, grass, 1, Vector(r.randrange(-5, 5), r.randrange(-5, 5)), 0, r.randrange(1, 4), 1, 0, 0))

#         regw(Button("idk", Vector(100, 100), Vector(200, 50), -1, border_color=Color(192, 31, 215), bg_color=Color(31, 2, 19), font="res/fonts/arial.ttf", text_color=Color(192, 31, 215), text="I don't know", font_size=20, thickness=5, action = lambda: print("I don't know"), hover_color=Color(60, 10, 80), click_color=Color(3, 10, 5)))

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
#         if Key.P in self.engine.released_keys:
#             self.engine.simulation_speed = 1 if self.engine.simulation_speed == 0 else 0



# Below is a flappy bird game, uncomment to run it ----------------------------



# class Player(Character):
#     def jump(self):
#         self.velocity.y = self.jump_velocity


#     def on_collision(self, collision_data):
#         super().on_collision(collision_data)

#         self.game_ref.die()


#     def tick(self, delta_time):
#         super().tick(delta_time)

#         if not -4.4 < self.position.y < 10:
#             self.game_ref.die()



# class Pipe(Actor):
#     def __init__(self, game_ref, name, position, material):
#         super().__init__(game_ref, name, Vector(1, 3), position, material=material)


#     def tick(self, delta_time):
#         super().tick(delta_time)

#         self.position.x -= 3 * delta_time

#         if self.position.x < -15:
#             self.game_ref.engine.destroy_actor(self.name)



# class ScoreUpdater(Actor):
#     def tick(self, delta_time):
#         super().tick(delta_time)

#         self.position.x -= 3 * delta_time

#         if self.position.x < -15:
#             self.game_ref.engine.destroy_actor(self.name)


#     def on_overlap_begin(self, other_actor):
#         super().on_overlap_begin(other_actor)
#         if other_actor.name != "Player":
#             return

#         self.game_ref.score += 1
#         self.game_ref.engine.simulation_speed += 0.01
#         self.game_ref.engine.widgets["score"].text = f"Score: {self.game_ref.score}"
#         self.game_ref.engine.destroy_actor(self.name)



# class Game(GameBase):
#     def begin_play(self):
#         super().begin_play()

#         eng = self.engine
#         regw = lambda widget: eng.register_widget(widget)
#         regb = lambda bg: eng.register_background(bg)
#         rega = lambda actor: eng.register_actor(actor)

#         bird_mat = Material("res/textures/birdie.png")
#         sky_mat = Material("res/textures/sky.png")

#         bgl_sky = BackgroundLayer(sky_mat, 15, 1)
#         regb(Background("sky", [bgl_sky]))
#         rega(Player(self, "Player" , Vector(0.5, 0.35), Vector(-7, 0), material=bird_mat, jump_velocity=5))
#         regw(Text("dead", Vector(0, 0), Vector(1600, 900), 1, "res/fonts/arial.ttf", Color(0, 0, 0, 100), False, "You died", Color(255,0,0), 100, Alignment.CENTER))
#         regw(Text("score", Vector(700, 10), Vector(200, 40), 2, "res/fonts/arial.ttf", Color(0, 0, 0, 100), True, "Score: 0", Color(255, 255, 255), 32, Alignment.CENTER))

#         eng.current_background = "sky"
#         eng.camera_position = Vector(0, 0)
#         eng.camera_width = 20
#         eng.console.handle_cmd("stat_all")

#         self.start()


#     def start(self):
#         self.engine.title = "Birdie"

#         self.pipe_mat = Material("res/textures/green.jpeg")

#         eng = self.engine
#         eng.actors["Player"].position = Vector(-7, 0)
#         eng.actors["Player"].velocity = Vector(0, 0)
#         eng.widgets["dead"].visible = False
#         eng.widgets["score"].text = "Score: 0"

#         self.index = 0
#         self.dead = False
#         eng.simulation_speed = 0
#         self.started = False
#         self.score = 0

#         self.clock = 0


#     def die(self):
#         self.engine.widgets["dead"].visible = True
#         self.dead = True
#         self.engine.simulation_speed = 0


#     def tick(self):
#         delta_time = super().tick()
#         if Key.ENTER in self.engine.released_keys and self.dead:
#             for actor in self.engine.actors:
#                 if actor != "Player":
#                     self.engine.destroy_actor(actor)
#             self.start()

#         if not self.dead and Key.P in self.engine.released_keys:
#             self.engine.simulation_speed = 1 if self.engine.simulation_speed == 0 else 1 + self.score * 0.01

#         if Key.ESC in self.engine.released_keys:
#             self.engine.running = False

#         if self.dead:
#             return
        
#         if not self.engine.running:
#             return
        
#         if not self.started:
#             if Key.SPACE in self.engine.released_keys:
#                 self.started = True
#                 self.engine.simulation_speed = 1
#             return
        
#         reg = lambda actor: self.engine.register_actor(actor)

#         if Key.SPACE in self.engine.released_keys:
#             self.engine.actors["Player"].jump()

#         self.clock += delta_time

#         if self.clock > 2:
#             offset = r.randrange(-2, 2)
#             self.clock = 0
#             self.index += 1

#             reg(Pipe(self,"Pipe_t_" + str(self.index), Vector(12, offset + 5), self.pipe_mat))
#             reg(Pipe(self,"Pipe_b_" + str(self.index), Vector(12, offset - 5), self.pipe_mat))
#             reg(ScoreUpdater(self, "ScoreUpdater_" + str(self.index), Vector(0.5, 2), Vector(12, 0), False, False, False))


        
