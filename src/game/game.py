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


#?ifdef SERVER
class TestLevel(Level):
    def __init__(self, engine_ref):
        actors = (
            Actor(engine_ref, "Ground", Vector(1, 1), Vector(0, -1), material = Material(Color(192, 31, 215))),
        )

        backgrounds = (
            Background("sky", (BackgroundLayer(Material(Color(192, 31, 215)), 20, .25),)),
        )

        super().__init__("Test_Level", Character, actors, backgrounds)

#?endif



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
class ServerGame(ServerGameBase):
    def __init__(self):
        super().__init__()

        self.engine.max_tps = 50

        self.engine.start_network("0.0.0.0", 5555, 10)

        self.engine.register_level(TestLevel(self.engine))

#?endif



