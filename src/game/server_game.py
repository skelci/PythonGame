#?attr SERVER

from engine.game_base import ServerGameBase

from components.level import Level
from components.game_math import *

from .blocks import *
from .tunnel_generator import TunnelGenerator
from .random_num import get_random_num

import noise
import random as r



TERRAIN_GENERATION_CHUNK_SIZE = 32
DEVIDER = TERRAIN_GENERATION_CHUNK_SIZE // CHUNK_SIZE



class TestLevel(Level):
    def __init__(self):
        super().__init__("Test_Level", TestPlayer, [], "sky")



#* This class was made by skelci
class KeyHandler:
    @staticmethod
    def key_W(engine_ref, level_ref, id, delta_time):
        level_ref.actors[engine_ref.get_player_actor(id)].jump()
    

    @staticmethod
    def key_A(engine_ref, level_ref, id, delta_time):
        level_ref.actors[engine_ref.get_player_actor(id)].move_direction = -1


    @staticmethod
    def key_D(engine_ref, level_ref, id, delta_time):
        level_ref.actors[engine_ref.get_player_actor(id)].move_direction = 1

    # Matevz
    @staticmethod
    def key_C(engine_ref, level_ref, id):
        # Spawn Entities at the player's position
        coal_entity = CoalEntity("coal_entity", Vector(-5, 26))
        gold_entity = GoldEntity("gold_entity", Vector(-4, 26))
        iron_entity = IronEntity("iron_entity", Vector(-3, 26))
        stone_entity = StoneEntity("stone_entity", Vector(-2, 26))
        dirt_entity = DirtEntity("dirt_entity", Vector(-1, 26))
        log_entity = LogEntity("log_entity", Vector(-6, 26))

        level_ref.register_actor(coal_entity)
        level_ref.register_actor(gold_entity)
        level_ref.register_actor(iron_entity)
        level_ref.register_actor(stone_entity)
        level_ref.register_actor(dirt_entity)
        level_ref.register_actor(log_entity)



class ServerGame(ServerGameBase):
    def __init__(self):
        super().__init__()
        self.engine.max_tps = 60
        self.seed = 1#random.randint(0, 9999)
        self.game_map = set()
        self.current_base_chunk = Vector(0, 0)
        self.tunnel_generator = TunnelGenerator(self.seed + 10)
    
        self.cave_seed = self.seed + 100
        self.ore_parameters = {
            "coal": {
                "scale": 0.042,
                "threshold": 0.72,  
                "base": self.seed + 500,        
                "min_depth": 15,
            },
            "iron": {
                "scale": 0.048,       
                "threshold": 0.76,
                "base": self.seed + 1000,
                "min_depth": 30,
            },
            "gold": {
                "scale": 0.052,    
                "threshold": 0.78,    
                "base": self.seed + 1500,
                "min_depth": 60,
            }
        }
        

        self.engine.register_level(TestLevel())

        self.engine.register_key(Keys.W, KeyPressType.HOLD, KeyHandler.key_W)
        self.engine.register_key(Keys.A, KeyPressType.HOLD, KeyHandler.key_A)
        self.engine.register_key(Keys.D, KeyPressType.HOLD, KeyHandler.key_D)
        self.engine.register_key(Keys.C, KeyPressType.TRIGGER, KeyHandler.key_C)
        self.engine.register_key(Keys.MOUSE_LEFT, KeyPressType.TRIGGER, breaking_blocks)

        #?ifdef ENGINE
        self.engine.console.handle_cmd("build_server")
        self.engine.console.handle_cmd("build_client")
        #?endif

        for x in range(-1, 2):
            for y in range(-1, 2):
                self.generate_and_load_chunks(x, y)

        self.engine.start_network("0.0.0.0", 5555, 10)
    

    #     MATEVŽ

    @staticmethod
    def smoothstep(val, edge0, edge1):
        t = max(0.0, min((val - edge0) / (edge1 - edge0), 1.0))
        return t * t * (3 - 2 * t)
    

    @staticmethod
    def tree_generation(self,chunk_origin, ground_level, pos, tree_threshold, shared_tree_positions, chunk_data):
        start_pos = chunk_origin + Vector(pos.x, pos.y)
        
        if get_random_num(self.seed,start_pos.x) < tree_threshold and start_pos.y == ground_level:
            can_spawn = True
            for tree_pos in shared_tree_positions:
                if abs(tree_pos.x - pos.x) < 4 and abs(tree_pos.y - pos.y) < 4:
                    can_spawn = False
                    break
               
            if can_spawn:
                shared_tree_positions.append(pos)
                tree_height = int(get_random_num(self.seed, pos.x, 5, 8))
                top = pos + Vector(0, tree_height)
                # Add trunk
                for h in range(1, tree_height + 1):
                    trunk_pos = pos + Vector(0, h)
                    if trunk_pos.y >= chunk_origin.y:
                        chunk_data.append(((trunk_pos.x, trunk_pos.y), "log"))
                #Pri matematiki pomagal Github Copilot
                # Add leaves
                rx = 3.25
                ry = 4.5
                top_leaf_pos = top + Vector(0, 4)
                chunk_data.append(((top_leaf_pos.x, top_leaf_pos.y), "leaf"))
                for dy in range(0, int(ry) + 1):
                    for dx in range(-int(rx), int(rx) + 1):
                        if (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry) <= 1:
                            leaf_pos = top + Vector(dx, dy-1)
                            chunk_data.append(((leaf_pos.x, leaf_pos.y), "leaf"))


    @staticmethod
    def ore_generation(ore_type, parameters, noise_data, ground_levels, chunk_data):
        ore_positions = set()
    
        for y_pos in range(TERRAIN_GENERATION_CHUNK_SIZE):
            for x_pos in range(TERRAIN_GENERATION_CHUNK_SIZE):
                pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                ground_level = ground_levels[x_pos]

                if (not is_cave and not is_tunnel and 
                pos.y <= ground_level - parameters["min_depth"] and 
                (pos.x, pos.y) not in ore_positions):
                    
                    ore_noise = noise.snoise2(
                        pos.x * parameters["scale"],
                        pos.y * parameters["scale"],
                        octaves=2,
                        persistence=0.5,
                        lacunarity=2.5,
                        base=parameters["base"]
                    )
                    
                    if ore_noise > parameters["threshold"]:
                        chunk_data.add(((pos.x, pos.y), ore_type))


    @staticmethod
    def generate_caves(self, chunk_origin, cave_scale_x, cave_scale_y, cave_octaves, cave_persistence,
                    surface_threshold, mid_threshold, deep_threshold, ground_levels, noise_data, smoothstep_func):
        for y_index in range(TERRAIN_GENERATION_CHUNK_SIZE):
            for x_index in range(TERRAIN_GENERATION_CHUNK_SIZE):
                pos = chunk_origin + Vector(x_index, y_index)
                ground_level = ground_levels[x_index]

                # Generate base noise and detail noise
                base_val = noise.snoise2(
                    pos.x * cave_scale_x,
                    pos.y * cave_scale_y,
                    octaves=cave_octaves,
                    persistence=cave_persistence,
                    lacunarity=2.0,
                    base=self.cave_seed
                )
                detail = noise.snoise2(
                    pos.x * cave_scale_x * 3,
                    pos.y * cave_scale_y * 3,
                    octaves=1,
                    base=self.cave_seed
                ) * 0.2
                combined_noise = base_val + detail

                # Calculate depth and determine cave threshold
                depth = ground_level - pos.y
                if depth < 6:
                    effective_threshold = surface_threshold
                elif 6 <= depth < 16:
                    effective_threshold = surface_threshold - (surface_threshold - mid_threshold) * smoothstep_func(depth, 6, 16)
                elif 16 <= depth < 30:
                    effective_threshold = mid_threshold - (mid_threshold - deep_threshold) * smoothstep_func(depth, 16, 30)
                else:
                    effective_threshold = deep_threshold

                # Determine if the position is part of a cave
                is_cave = combined_noise > effective_threshold and pos.y < ground_level
                noise_data[y_index][x_index] = (pos, is_cave, False)



    def generate_chunk(self, x, y):
        chunk_origin = Vector(x, y) * TERRAIN_GENERATION_CHUNK_SIZE
        terrain_scale = 0.02
        
        
        ground_levels = []
        for x_pos in range(TERRAIN_GENERATION_CHUNK_SIZE):
            pos_x = chunk_origin.x + x_pos
            height_noise = noise.pnoise1(pos_x * terrain_scale, repeat=9999999, base=self.seed)
            ground_levels.append(16 - math.floor(height_noise * 15))
           

        cave_scale_x = 0.02
        cave_scale_y = 0.025
        surface_threshold = 0.6
        mid_threshold = 0.5      
        deep_threshold = 0.34  
        cave_octaves = 2
        cave_persistence = 0.5
    
    
        noise_data = [[None for _ in range(TERRAIN_GENERATION_CHUNK_SIZE)] for _ in range(TERRAIN_GENERATION_CHUNK_SIZE)]
        
        self.generate_caves(
            self, chunk_origin, cave_scale_x, cave_scale_y, cave_octaves, cave_persistence,
            surface_threshold, mid_threshold, deep_threshold, ground_levels, noise_data, ServerGame.smoothstep
        )

        chunk_data = []
                        
        # Generate tunnels
        if y <= 0:
            tunnel_gen = self.tunnel_generator
            tunnel_gen.generate_tunnels(noise_data, ground_levels)

            # Add tunnel tiles to chunk_data
            for y_pos in range(TERRAIN_GENERATION_CHUNK_SIZE):
                for x_pos in range(TERRAIN_GENERATION_CHUNK_SIZE):
                    pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                    if is_tunnel:
                        chunk_data.append([(pos.x, pos.y), None])


        # Generate ores
        for ore_type, parameters in self.ore_parameters.items():
            ore_chunk_data = set()
            self.ore_generation(ore_type, parameters, noise_data, ground_levels, ore_chunk_data)
            chunk_data.extend([(pos, ore_type) for pos, ore_type in ore_chunk_data])
            

        tree_positions = [] 
        tree_threshold = 0.05
            
        for y_pos in range(TERRAIN_GENERATION_CHUNK_SIZE):
            for x_pos in range(TERRAIN_GENERATION_CHUNK_SIZE):

                pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                ground_level = ground_levels[x_pos]
                if any(block[0] == (pos.x, pos.y) for block in chunk_data):
                    continue

                if is_cave:
                    continue
                elif pos.y == ground_level:
                    self.tree_generation(self, chunk_origin,ground_level, pos, tree_threshold, tree_positions, chunk_data)
                    chunk_data.append([(pos.x, pos.y), "grass"])
                    
                elif pos.y < ground_level and pos.y > ground_level - 5:
                    chunk_data.append([(pos.x, pos.y), "dirt"])
                elif pos.y <= ground_level - 5: 
                    chunk_data.append([(pos.x, pos.y), "stone"])

        return chunk_data
    

    def generate_and_load_chunks(self, chunk_x, chunk_y):
        level = self.engine.levels.get("Test_Level")
        if level is None:
            return

        target_chunk = Vector(chunk_x, chunk_y)
        
        if target_chunk not in self.game_map:
            self.game_map.add(target_chunk)
            chunk_thread = threading.Thread(target=self.load_chunk, args=(chunk_x, chunk_y, level))
            chunk_thread.start()



    def load_chunk(self, chunk_x, chunk_y, level):
        
        chunk_data = self.generate_chunk(chunk_x, chunk_y)
        
       
        actors_to_add = []
        for tile in chunk_data:
            pos, tile_type = tile
            actor_name = f"{tile_type}_{pos[0]}_{pos[1]}"
            new_actor = None
            
            if tile_type == "grass":
                new_actor = Grass(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "log":
                new_actor = Log(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "leaf":
                new_actor = Leaf(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "dirt":
                new_actor = Dirt(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "stone":
                new_actor = Stone(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "coal":
                new_actor = Coal(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "gold":
                new_actor = Gold(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "iron":
                new_actor = Iron(actor_name, Vector(pos[0], pos[1]))
            elif tile_type == "tunnel_debug":
                new_actor = DebugTunnel(actor_name, Vector(pos[0], pos[1]))
            if new_actor is not None:
                actors_to_add.append(new_actor)
        
        for actor in actors_to_add:
            level.register_actor(actor)
            

    def tick(self):
        delta_time = super().tick()
        
        
        current_level = self.engine.levels.get("Test_Level")
        if not current_level:
            return
        
        # Collect player positions
        positions = []
        for player_id, player_actor in current_level.actors.items():
            if isinstance(player_actor, TestPlayer):
                positions.append(player_actor.position)

        if not positions:
            return
        

        for pos in positions:
            new_base_chunk = ((pos + TERRAIN_GENERATION_CHUNK_SIZE/2) / TERRAIN_GENERATION_CHUNK_SIZE).floored
        

        
            # Load chunks in radius
            chunks_to_load = []
            ud = 0
            if self.engine.players:
                for player in self.engine.players.values():
                    ud += player.update_distance
                    ud = (ud // DEVIDER) + 1
                    for offset_y in range(-ud - 2, ud + 3):
                        for offset_x in range(-ud - 2, ud + 3):
                            chunks_to_load.append((
                                new_base_chunk.x + offset_x, 
                                new_base_chunk.y + offset_y
                            ))

            for base_chunk_x, base_chunk_y in chunks_to_load:
                self.generate_and_load_chunks(base_chunk_x, base_chunk_y)


#    JURE

Indestructible_classes = (
    "LeafEntity", "StickEntity", "LogEntity", "GrassEntity", 
    "DirtEntity", "StoneEntity", "CoalEntity", "IronEntity", "GoldEntity"
)
def breaking_blocks(engine_ref, level_ref, id):
    
    #print('breaking_blocks')
    # Get the player's position
    player = level_ref.actors[engine_ref.get_player_actor(id)].position
    #chunk_x, chunk_y=engine_ref.players[id].previous_chunk.rounded

    function_3x3=level_ref.get_actors_in_chunks_3x3(get_chunk_cords(player))
    #print(function_3x3)


    #Get the mouse position 
    mouse_pos = engine_ref.players[id].world_mouse_pos
    mouse_pos = mouse_pos.rounded
    # print(mouse_pos)   

    #allowed to break this blocks
    #allowed_blocks=tuple(("grass", "dirt", "stone", "log", "leaves", "Leaves", "LEAVES", "leaf", "Leaf", "LEAF", "Coal", "Iron", "Gold"))

    for actor in function_3x3:
        #print(actor)
        actor_position = actor.position.rounded
        #print(actor_position)
        #print("actor class", actor.__class__.__name__)

        if actor_position == mouse_pos:
            #print('actor:', actor_position)
            #print(EntityPosition)
            #print(Indestructible_classes)
            if actor.__class__.__name__ in Indestructible_classes:
                #print('indestructible')
                break

            if actor.name.startswith("__Player_"):
                break
            
            engine_ref.levels["Test_Level"].destroy_actor(actor)          
            break

