from enginet.game_base import *

from componentst.actor import Actor
from componentst.rigidbody import Rigidbody
from componentst.datatypes import *
from componentst.material import Material
from componentst.character import Character
from componentst.button import Button
from componentst.background import *
from componentst.text import Text
from componentst.level import Level

import random as r
#TODO change every isubclass to isinstance


#?ifdef SERVER
class TestLevel(Level):
    def __init__(self, engine_ref):
        actors = (
            Actor(engine_ref, "Ground", Vector(1, 1), Vector(0, -1), material = Material("./res/textures/grass.jpeg")),
        )

        backgrounds = (
            Background("sky", (BackgroundLayer(Material("./res/textures/sky.png"), 20, .25),)),
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



