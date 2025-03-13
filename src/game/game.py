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
#TODO change every isubclass to isinstance



#?ifdef CLIENT
class ClientGame(ClientGameBase):
    def __init__(self):
        super().__init__()

        self.engine.camera_width = 48

        self.engine.connect("localhost", 5555)

        self.clock_1s = 0

        self.current_level = None

        self.engine.show_all_stats()


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

#?endif



#?ifdef SERVER
class TestPlayer(Character):
    def __init__(self, engine_ref, name):
        super().__init__(engine_ref, name, position=Vector(2, 0), material = Material(Color(0, 0, 255)))



class TestLevel(Level):
    def __init__(self, engine_ref):
        actors = (
            Actor(engine_ref, "Ground", Vector(1, 1), Vector(0, -1), material = Material(Color(192, 31, 215))),
        )

        backgrounds = (
            Background("sky", (BackgroundLayer(Material("res/textures/sky.png"), 20, .25),)),
        )

        super().__init__("Test_Level", Character, actors, backgrounds)



class KeyHandler:
    @staticmethod
    def key_W(engine_ref, id):
        engine_ref.levels[engine_ref.players[id].level].actors[engine_ref.get_player_actor(id)].jump()
    

    @staticmethod
    def key_A(engine_ref, id):
        engine_ref.levels[engine_ref.players[id].level].actors[engine_ref.get_player_actor(id)].move_direction = -1


    @staticmethod
    def key_D(engine_ref, id):
        engine_ref.levels[engine_ref.players[id].level].actors[engine_ref.get_player_actor(id)].move_direction = 1



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


#Log, Rock, Coal, Iron, Gold, Diamond, Copper, Silver, Copper, Leaves
class Log(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Log", position, material = Material(Color(139, 69, 19)))

    def __del__(self):
        print("Log has been destroyed")

class Rock(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Rock", position, material = Material(Color(128, 128, 128)))

    def __del__(self):
        print("Rock has been destroyed")

class Coal(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Coal", position, material = Material(Color(0, 0, 0)))  

    def __del__(self):
        print("Coal has been destroyed")

class iron(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Iron", position, material = Material(Color(255, 0, 0)))  

    def __del__(self):
        print("Iron has been destroyed")

class Gold(Actor):  
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Gold", position, material = Material(Color(255, 215, 0)))  

    def __del__(self):
        print("Gold has been destroyed")   

class diamond(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Diamond", position, material = Material(Color(0, 191, 255)))  

    def __del__(self):
        print("Diamond has been destroyed")

class copper(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Copper", position, material = Material(Color(184, 115, 51)))  

    def __del__(self):
        print("Copper has been destroyed")

class Silver(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Silver", position, material = Material(Color(192, 192, 192)))  

    def __del__(self):
        print("Silver has been destroyed")

class copper(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Copper", position, material = Material(Color(184, 115, 51)))  

    def __del__(self):
        print("Copper has been destroyed")

class leaves(Actor):
    def __init__(self, engine_ref, position):
        super().__init__(engine_ref, "Leaves", position, material = Material(Color(0, 255, 0)))  

    def __del__(self):
        print("Leaves has been destroyed")

        