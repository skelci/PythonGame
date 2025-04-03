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
import math
import noise


CHUNK_SIZE = 8
CAMERA_OFFSET_X = 1
CAMERA_OFFSET_Y = 1


class Log(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5),collidable=False, material = Material(Color(139, 69, 19)))
        self.position = position

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

class Coal(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/coal_ore.png"))
        self.position = position

class Iron(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/iron_ore.png"))
        self.position = position

class Gold(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/gold_ore.png"))
        self.position = position


class TestPlayer(Character):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position=Vector(-5, 25), material = Material(Color(0, 0, 255)), jump_velocity=7)



#?ifdef CLIENT
class ClientGame(ClientGameBase):
    def __init__(self):
        super().__init__()

        self.true_scroll = [0, 0]
        self.game_map = {}
        self.loaded_chunks = set()

        eng = self.engine

        eng.set_camera_width(16 * 8)
        eng.resolution = Vector(1600, 900)

        eng.connect("localhost", 5555)
        # eng.fullscreen=True

        self.clock_1s = 0

        self.current_level = None

        eng.show_all_stats()
        #eng.hide_all_stats()

        eng.add_actor_template(TestPlayer)
        eng.add_actor_template(Log)
        eng.add_actor_template(Grass)
        eng.add_actor_template(Dirt)
        eng.add_actor_template(Stone)
        eng.add_actor_template(Coal)
        eng.add_actor_template(Iron)
        eng.add_actor_template(Gold)
    
        eng.register_background(Background("sky", (BackgroundLayer(Material(Color(100, 175, 255)), 20, 0.25), )))




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
 
            # Smooth chase camera: adjust true_scroll to follow the player.
            self.true_scroll[0] += (player.position.x - self.true_scroll[0] - CAMERA_OFFSET_X) * 0.1
            self.true_scroll[1] += (player.position.y - self.true_scroll[1] - CAMERA_OFFSET_Y) * 0.1
            
            # Update the camera position of the engine so that rendering follows.
            self.engine.camera_position = Vector(
                self.true_scroll[0],
                self.true_scroll[1]
            )                      

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

        self.engine.max_tps = 60

        self.engine.start_network("0.0.0.0", 5555, 10)

        self.engine.register_level(TestLevel(self.engine))

        self.engine.register_key(Keys.W, KeyPressType.HOLD, KeyHandler.key_W)
        self.engine.register_key(Keys.A, KeyPressType.HOLD, KeyHandler.key_A)
        self.engine.register_key(Keys.D, KeyPressType.HOLD, KeyHandler.key_D)


        self.game_map = {}
        self.loaded_chunks = set()


    @staticmethod
    def ridged_multifractal(x, y, octaves=4, lacunarity=2.0, gain=0.5, offset=1.0):
        frequency = 1.0
        amplitude = 0.5
        weight = 1.0
        result = 0.0
        for i in range(octaves):
            n = noise.snoise2(x * frequency, y * frequency)  # noise in [-1,1]
            n = abs(n)           # ridging: absolute value
            n = offset - n       # invert so ridges show up
            n = n * n            # square to accentuate
            n *= weight
            result += n * amplitude
            weight = n * gain
            weight = max(min(weight, 1.0), 0.0)  # clamp weight [0,1]
            frequency *= lacunarity
            amplitude *= gain
        return result

    def generate_chunk(self, x, y):
        chunk_data = []
        chunk_origin = Vector(x, y) * CHUNK_SIZE
        tree_threshold = 0.1  # chance of a tree being generated on a grass tile
        """
        Cave scale (cave_scale_x and cave_scale_y) acts as a multiplier for the noise coordinates
        when generating cave patterns. Lower values result in larger, smoother cave features, 
        while higher values create more detailed and smaller variations in the caves."""
        cave_scale_x = 0.044
        cave_scale_y = 0.044
        cave_threshold_surface = 0.4# Higher threshold to prevent big openings at surface
        cave_threshold_deep = 0.3  # Higher threshold, fewer caves

        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                pos = chunk_origin + Vector(x_pos, y_pos)
                # Noise-based height for a given x position.
                height_noise = noise.pnoise1((x_pos + chunk_origin.x) * 0.035, repeat=9999999, base=0)
                height_val = math.floor(height_noise * 10)
                ground_level = 16 - height_val

                # Use ridged multifractal noise to generate cave patterns (narrower caves)
                cave_val = self.ridged_multifractal(
                    (x_pos + chunk_origin.x) * cave_scale_x,
                    (y_pos + chunk_origin.y) * cave_scale_y,
                    octaves=4, lacunarity=1.8, gain=0.5, offset=1.0
                )

                # Only allow caves below ground level, but avoid massive caves
                if pos.y > ground_level - 15:  # Surface caves
                    if cave_val > cave_threshold_surface:
                        continue  # Make surface caves smaller
                elif pos.y > ground_level - 30:  # Transition zone
                    if cave_val > (cave_threshold_surface + cave_threshold_deep) / 2:
                        continue
                else:  # Deep caves
                    if cave_val > cave_threshold_deep:
                        continue  # Allow deeper, but not too open

                # Determine tile type based on height level
                tile_type = None
                if pos.y == ground_level:
                    tile_type = "grass"
                    if r.random() < tree_threshold:
                        tree_height = r.randint(4, 7)
                        for h in range(1, tree_height + 1):
                            trunk_pos = pos + Vector(0, h)
                            if trunk_pos.y >= chunk_origin.y:
                                chunk_data.append([(trunk_pos.x, trunk_pos.y), "log"])

                if pos.y < ground_level and pos.y > ground_level - 5:
                    tile_type = "dirt"
                if pos.y <= ground_level - 5:
                    tile_type = "stone"
                if pos.y <= ground_level - 10:
                    if r.random() < 0.02:
                        tile_type = "coal"
                if pos.y <= ground_level - 20:
                    if r.random() < 0.01:
                        tile_type = "iron"
                if pos.y <= ground_level - 35:
                    if r.random() < 0.005:
                        tile_type = "gold"

                # Add tile to chunk data
                if tile_type is not None:
                    chunk_data.append([(pos.x, pos.y), tile_type])

        return chunk_data

    
    def generate_and_load_chunks(self, chunk_x, chunk_y):
        level = self.engine.levels.get("Test_Level")
        if level is None:
            return

        actors_to_add = []
        target_chunk = f"{chunk_x};{chunk_y}"
                        

        if target_chunk not in self.game_map:
            self.game_map[target_chunk] = self.generate_chunk(chunk_x, chunk_y)


        if target_chunk not in self.loaded_chunks:
            for tile in self.game_map[target_chunk]:
                pos, tile_type = tile
                actor_name = f"{tile_type}_{pos[0]}_{pos[1]}"
                new_actor = None

                if tile_type == "grass":
                    new_actor = Grass(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "log":
                    new_actor = Log(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "dirt":
                    new_actor = Dirt(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "stone":
                    new_actor = Stone(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "coal":
                    new_actor = Coal(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "gold":
                    new_actor = Gold(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "iron":
                    new_actor = Iron(self.engine, actor_name, Vector(pos[0], pos[1]))
                

                if new_actor is not None:
                    actors_to_add.append(new_actor)

            self.loaded_chunks.add(target_chunk)

        for actor in actors_to_add:
            level.register_actor(actor)


    def tick(self):
        delta_time = super().tick()
        if delta_time > 0.2: print(f"Server tick took {delta_time} seconds.")
        current_level = self.engine.levels.get("Test_Level")
        if not current_level:
            return
        
        # Collect the positions of all TestPlayers.
        positions = []
        for player_id, player_actor in current_level.actors.items():
            if isinstance(player_actor, TestPlayer):
                positions.append(player_actor.position)

        if not positions:
            return
        
        # Average the player positions.
        avg_x = sum(p.x for p in positions) / len(positions)
        avg_y = sum(p.y for p in positions) / len(positions)
        avg_pos = Vector(avg_x, avg_y)

        new_base_chunk = Vector(
            math.floor((avg_pos.x + CHUNK_SIZE/2) / CHUNK_SIZE),
            math.floor((avg_pos.y + CHUNK_SIZE/2) / CHUNK_SIZE)
        )

        # Smooth out abrupt changes by interpolating toward the new base chunk.
        if not hasattr(self, "current_base_chunk"):
            self.current_base_chunk = new_base_chunk
        else:
            smoothing_factor = 0.5 # Adjust this factor to control smoothness.
            self.current_base_chunk += (new_base_chunk - self.current_base_chunk) * smoothing_factor

        base_chunk_vector = self.current_base_chunk.floored
        
        # Create a symmetric grid of chunks around the smoothed base chunk.
        chunks_to_load = []
        ud = 0
        if self.engine.players:
            for player in self.engine.players.values():
                ud += player.update_distance
        ud //= len(self.engine.players)
        for offset_y in range(-ud, ud + 1):
            for offset_x in range(-ud, ud + 1):
                chunks_to_load.append((base_chunk_vector.x + offset_x, base_chunk_vector.y + offset_y))

        for base_chunk_x, base_chunk_y in chunks_to_load:
            self.generate_and_load_chunks(base_chunk_x, base_chunk_y)