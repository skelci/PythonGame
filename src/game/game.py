from engine.game_base import *

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.datatypes import *
from components.material import Material
from components.character import Character
from components.button import Button
from components.background import *
from components.text import Text
from components.level import Level

import random as r

class Grass(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material(Color(0, 255, 0)))
        self.position = position

class Dirt(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/dirt.png"))
        self.position = position

class TestPlayer(Character):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position=Vector(0, 3), material = Material(Color(0, 0, 255)))


#?ifdef CLIENT
class ClientGame(ClientGameBase):
    def __init__(self):
        super().__init__()

        eng = self.engine

        eng.camera_width = 48

        eng.connect("localhost", 5555)

        self.clock_1s = 0

        self.current_level = None

        eng.show_all_stats()

        eng.add_actor_template(TestPlayer)
        eng.add_actor_template(Grass)

        eng.register_background(Background("sky", (BackgroundLayer(Material("res/textures/sky.png"), 20, 0.25), )))

        self.engine.add_actor_template(TestPlayer)
        self.engine.add_actor_template(Grass)
        self.engine.add_actor_template(Dirt)

    def tick(self):
        delta_time = super().tick()

        self.clock_1s += delta_time

        if self.engine.network.id == -1:
            if self.clock_1s > 1:
                self.clock_1s = 0
                self.engine.network.send("login", ("username", "password"))
                self.engine.network.send("register", ("username", "password"))
            return
        
        if not self.current_level:
            self.current_level = "Test_Level"
            self.engine.join_level(self.current_level)
            return
        if f"__Player_{self.engine.network.id}" in self.engine.level.actors:
            self.engine.camera_position = self.engine.level.actors[f"__Player_{self.engine.network.id}"].position

#?endif



#?ifdef SERVER
class TestLevel(Level):
    def __init__(self, engine_ref):
        actors = (
        )
        # Grass and dirt
        for i in range(-24, 25):
            actors += (Grass(engine_ref, "Grass_" + str(i), Vector(i, -1))),
            for j in range(-2, -14, -1):
                actors += (Dirt(engine_ref, "Dirt_" + str(i) + str(j), Vector(i, j))),
        
       
        super().__init__("Test_Level", TestPlayer, actors, "sky")



class KeyHandler:
    @staticmethod
    def key_W(engine_ref, level_ref, id):
        level_ref.actors[engine_ref.get_player_actor(id)].jump()
    

    @staticmethod
    def key_A(engine_ref, level_ref, id):
        level_ref.actors[engine_ref.get_player_actor(id)].move_direction = -1


    @staticmethod
    def key_D(engine_ref, level_ref, id):
        level_ref.actors[engine_ref.get_player_actor(id)].move_direction = 1



class ServerGame(ServerGameBase):
    def __init__(self):
        super().__init__()

        self.engine.max_tps = 50

        self.engine.start_network("0.0.0.0", 5555, 10)

        self.engine.register_level(TestLevel(self.engine))

        self.engine.register_key(Keys.W, KeyPressType.HOLD, KeyHandler.key_W)
        self.engine.register_key(Keys.A, KeyPressType.HOLD, KeyHandler.key_A)
        self.engine.register_key(Keys.D, KeyPressType.HOLD, KeyHandler.key_D)


#?endif
