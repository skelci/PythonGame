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


TILE_SIZE = 64
CHUNK_SIZE = 16
CAMERA_OFFSET_X = 152
CAMERA_OFFSET_Y = 106


class Grass(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/grass_block.png"))
        self.position = position

class Dirt(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/dirt.png"))
        self.position = position
class Stone(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/stone.png"))
        self.position = position

class TestPlayer(Character):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position=Vector(0, 3), material = Material(Color(0, 0, 255)))



#?ifdef CLIENT
class ClientGame(ClientGameBase):
    def __init__(self):
        super().__init__()

        self.true_scroll = [0, 0]
        self.game_map = {}
        self.loaded_chunks = set()

        eng = self.engine

        eng.camera_width = 48

        eng.connect("localhost", 5555)

        self.clock_1s = 0

        self.current_level = None

        eng.show_all_stats()

        eng.add_actor_template(TestPlayer)
        eng.add_actor_template(Grass)
        eng.add_actor_template(Dirt)
        eng.add_actor_template(Stone)

        eng.register_background(Background("sky", (BackgroundLayer(Material("res/textures/sky.png"), 20, 0.25), )))

        self.engine.add_actor_template(TestPlayer)
        self.engine.add_actor_template(Grass)
        self.engine.add_actor_template(Dirt)
        self.engine.add_actor_template(Stone)

            #CHUNK GENERATION


    def generate_chunk(self, x, y):
        chunk_data = []
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                global_x = x * CHUNK_SIZE + x_pos
                global_y = y * CHUNK_SIZE + y_pos
                tile_type = None
                if global_y == -2:
                    tile_type = "grass"
                elif global_y < -2 and global_y >= -5:
                    tile_type = "dirt"
                elif global_y < -5:
                    tile_type = "stone"
                if tile_type is not None:
                    chunk_data.append([(global_x, global_y), tile_type])
        return chunk_data



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
        
        player_key = f"__Player_{self.engine.network.id}"
        if player_key in self.engine.level.actors:
            player = self.engine.level.actors[player_key]
            
             # Align and smooth camera motion
            self.engine.camera_position = player.position
            self.engine.camera_position = Vector(
                self.engine.camera_position.x + (player.position.x - self.engine.camera_position.x) / 10,
                self.engine.camera_position.y + (player.position.y - self.engine.camera_position.y) / 10
            )
        else:
            return
        
        self.true_scroll[0] += (self.engine.camera_position.x - self.true_scroll[0] - CAMERA_OFFSET_X) /20
        self.true_scroll[1] += (self.engine.camera_position.y - self.true_scroll[1] - CAMERA_OFFSET_Y) /20
        scroll = [int(self.true_scroll[0]), int(self.true_scroll[1])]


         # Pre-compute divisor and calculate base chunk coordinates
        chunk_divisor = CHUNK_SIZE * TILE_SIZE
        base_chunk_x = int(round(scroll[0] / chunk_divisor))
        base_chunk_y = int(round(scroll[1] / chunk_divisor))

        actors_to_add = []
        existing_names = set(self.engine.level.actors.keys())

        # Generate and load all chunks in a 3x4 grid around the player
        for offset_y in range(-1, 2):
            for offset_x in range(-1, 3):
                target_x = base_chunk_x + offset_x
                target_y = base_chunk_y + offset_y
                target_chunk = f"{target_x};{target_y}"
                if target_chunk not in self.game_map:
                    self.game_map[target_chunk] = self.generate_chunk(target_x, target_y)
                if target_chunk not in self.loaded_chunks:
                    for tile in self.game_map[target_chunk]:
                        actor_name = ""
                        new_actor = None
                        if tile[1] == "grass":
                            actor_name = f"Grass_{tile[0][0]}_{tile[0][1]}"
                            new_actor = Grass(self.engine, actor_name, Vector(tile[0][0], tile[0][1]))
                        elif tile[1] == "dirt":
                            actor_name = f"Dirt_{tile[0][0]}_{tile[0][1]}"
                            new_actor = Dirt(self.engine, actor_name, Vector(tile[0][0], tile[0][1]))
                        elif tile[1] == "stone":
                            actor_name = f"Stone_{tile[0][0]}_{tile[0][1]}"
                            new_actor = Stone(self.engine, actor_name, Vector(tile[0][0], tile[0][1]))
                        if new_actor is not None and actor_name not in existing_names:
                            actors_to_add.append(new_actor)
                            existing_names.add(actor_name)
                    self.loaded_chunks.add(target_chunk)

        # Add all newly created actors at once
        for actor in actors_to_add:
            self.engine.level.actors[actor.name] = actor
                                    

#?endif



#?ifdef SERVER
class TestLevel(Level):
    def __init__(self, engine_ref):


       
        super().__init__("Test_Level", TestPlayer, [], "sky")



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
