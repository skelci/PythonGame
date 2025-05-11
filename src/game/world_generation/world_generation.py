#?attr SERVER

from engine.datatypes import *

from game.helper_functions import get_random_num
from game.blocks import *
from .tunnel_generator import TunnelGenerator

import noise



class WorldGeneration:
    def __init__(self, level_ref, seed):
        self.level_ref = level_ref
        self.seed = seed
        self.game_map = set()
        self.tunnel_generator = TunnelGenerator(self.seed + 1)
        self.cave_seed = self.seed + 2
        self.tree_seed = self.seed + 3
        self.grass_seed = self.seed + 4
        self.chunk_size = 32

        self.ore_parameters = {
            "coal": {
                "scale": 0.042,
                "threshold": 0.77,
                "base": self.seed,
                "min_depth": 10,
            },
            "iron": {
                "scale": 0.045,
                "threshold": 0.76,
                "base": self.seed + 500,
                "min_depth": 20,
            },
            "gold": {
                "scale": 0.052,
                "threshold": 0.8,
                "base": self.seed + 1000,
                "min_depth": 40,
            },
            "diamond": {
                "scale": 0.055,
                "threshold": 0.8,
                "base": self.seed + 1500,
                "min_depth": 10,
            },
        }

    def tree_generation(self, chunk_origin, ground_level, pos, tree_threshold, shared_tree_positions, chunk_data):
        start_pos = chunk_origin + Vector(pos.x, pos.y)

        if get_random_num(self.tree_seed, start_pos.x) < tree_threshold and start_pos.y == ground_level and "sand" not in chunk_data.get((pos.x, pos.y), []):
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
                        if (trunk_pos.x, trunk_pos.y) not in chunk_data:
                            chunk_data[(trunk_pos.x, trunk_pos.y)] = []
                        if "log" not in chunk_data[(trunk_pos.x, trunk_pos.y)]:
                            chunk_data[(trunk_pos.x, trunk_pos.y)].append("log")
                # Add leaves
                rx = 3.25
                ry = 4.5
                top_leaf_pos = top + Vector(0, 4)
                if (top_leaf_pos.x, top_leaf_pos.y) not in chunk_data:
                    chunk_data[(top_leaf_pos.x, top_leaf_pos.y)] = []
                if "leaf" not in chunk_data[(top_leaf_pos.x, top_leaf_pos.y)]:
                    chunk_data[(top_leaf_pos.x, top_leaf_pos.y)].append("leaf")
                for dy in range(0, int(ry) + 1):
                    for dx in range(-int(rx), int(rx) + 1):
                        if (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry) <= 1:
                            leaf_pos = top + Vector(dx, dy - 1)
                            if (leaf_pos.x, leaf_pos.y) not in chunk_data:
                                chunk_data[(leaf_pos.x, leaf_pos.y)] = []
                            if "leaf" not in chunk_data[(leaf_pos.x, leaf_pos.y)]:
                                chunk_data[(leaf_pos.x, leaf_pos.y)].append("leaf")


    def grass_generation(self, chunk_origin, ground_level, pos, grass_threshold, shared_grass_positions, chunk_data):
        start_pos = chunk_origin + Vector(pos.x, pos.y)

        if get_random_num(self.grass_seed, start_pos.x) < grass_threshold and start_pos.y == ground_level and "sand" not in chunk_data.get((pos.x, pos.y), []):
            shared_grass_positions.append(pos)
            if (pos.x, pos.y + 1) not in chunk_data or "log" in chunk_data[(pos.x, pos.y + 1)]:
                chunk_data[(pos.x, pos.y + 1)] = ["grass"]
    
    def sand_generation(self, pos, ground_level, sand_threshold, chunk_data):

        noise_val = noise.snoise2(
            pos.x * 0.018,
            pos.y * 0.03,
            octaves=1,
            base=self.seed + 50,
        )
        if noise_val > sand_threshold and pos.y > ground_level - 8:
            if "dirt" in chunk_data.get((pos.x, pos.y), []) or "grass_block" in chunk_data.get((pos.x, pos.y), []) or "stone" in chunk_data.get((pos.x, pos.y), []):
                chunk_data[(pos.x, pos.y)] = ["sand"]


    def ore_generation(self, ore_type, parameters, noise_data, ground_levels, chunk_data):
        for y_pos in range(self.chunk_size):
            for x_pos in range(self.chunk_size):
                pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                ground_level = ground_levels[x_pos]

                if (
                    not is_cave
                    and not is_tunnel
                    and pos.y <= ground_level - parameters["min_depth"]
                    and (pos.x, pos.y) not in chunk_data
                ):
                    ore_noise = noise.snoise2(
                        pos.x * parameters["scale"],
                        pos.y * parameters["scale"],
                        octaves=2,
                        persistence=0.5,
                        lacunarity=2.5,
                        base=parameters["base"],
                    )

                    if ore_noise > parameters["threshold"]:
                        chunk_data[(pos.x, pos.y)] = ore_type

    def generate_caves(self, chunk_origin, cave_scale_x, cave_scale_y, cave_octaves, cave_persistence, ground_levels, noise_data):
        for y_index in range(self.chunk_size):
            for x_index in range(self.chunk_size):
                pos = chunk_origin + Vector(x_index, y_index)
                ground_level = ground_levels[x_index]

                # Generate base noise and detail noise
                base_val = noise.snoise2(
                    pos.x * cave_scale_x,
                    pos.y * cave_scale_y,
                    octaves=cave_octaves,
                    persistence=cave_persistence,
                    lacunarity=2.0,
                    base=self.cave_seed,
                )
                detail = noise.snoise2(
                    pos.x * cave_scale_x * 3,
                    pos.y * cave_scale_y * 3,
                    octaves=1,
                    base=self.cave_seed,
                ) * 0.2
                combined_noise = base_val + detail

                depth = ground_level - pos.y
                if depth < 4:
                    effective_threshold = 0.9
                elif 4 <= depth < 15:
                    effective_threshold = 0.6
                elif 15 <= depth < 30:
                    effective_threshold = 0.5
                elif 30 <= depth < 50:
                    effective_threshold = 0.4
                else:
                    effective_threshold = 0.35

                is_cave = combined_noise > effective_threshold and pos.y < ground_level
                noise_data[y_index][x_index] = (pos, is_cave, False)

    def generate_chunk(self, chunk):
        chunk_origin = chunk * self.chunk_size
        terrain_scale = 0.03
        dirt_scale = 0.03

        dirt_levels = []
        ground_levels = []
        for x_pos in range(self.chunk_size):
            pos_x = chunk_origin.x + x_pos
            terrain_height_noise = noise.pnoise1(pos_x * terrain_scale, repeat=2**16, base=self.seed)
            ground_levels.append(16 - math.floor(terrain_height_noise * 20))

            dirt_height_noise = noise.pnoise1(pos_x * dirt_scale, repeat=2**16, base=self.seed)
            dirt_levels.append(10 - math.floor(dirt_height_noise * 15))

        cave_scale_x = 0.02
        cave_scale_y = 0.025
        cave_octaves = 2
        cave_persistence = 0.5

        noise_data = [[None for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]

        self.generate_caves(chunk_origin, cave_scale_x, cave_scale_y, cave_octaves, cave_persistence, ground_levels, noise_data)

        chunk_data = {}

        # Generate tunnels
        if chunk.y <= 0:
            self.tunnel_generator.generate_tunnels(noise_data, ground_levels)

        # Generate ores
        for ore_type, parameters in self.ore_parameters.items():
            self.ore_generation(ore_type, parameters, noise_data, ground_levels, chunk_data)

        tree_positions = []
        tree_threshold = 0.04

        grass_positions = []
        grass_threshold = 0.1

        sand_threshold = 0.48

        for y_pos in range(self.chunk_size):
            for x_pos in range(self.chunk_size):
                pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                ground_level = ground_levels[x_pos]
                dirt_level = dirt_levels[x_pos]

                if (pos.x, pos.y) in chunk_data:
                    continue

                if is_cave:
                    continue
                elif pos.y == ground_level:
                    chunk_data[(pos.x, pos.y)] = ["grass_block"]
                elif pos.y < ground_level and pos.y > dirt_level:
                    chunk_data[(pos.x, pos.y)] = ["dirt"]
                elif pos.y <= dirt_level:
                    chunk_data[(pos.x, pos.y)] = ["stone"]

                self.sand_generation(pos, ground_level, sand_threshold, chunk_data)
                self.tree_generation(chunk_origin, ground_level, pos, tree_threshold, tree_positions, chunk_data)
                self.grass_generation(chunk_origin, ground_level, pos, grass_threshold, grass_positions, chunk_data)

        return chunk_data

    def generate_and_load_chunks(self, chunk):

        if chunk not in self.game_map:
            self.game_map.add(chunk)
            chunk_thread = threading.Thread(target=self.load_chunk, args=(chunk,))
            chunk_thread.start()


    def load_chunk(self, chunk):
        chunk_data = self.generate_chunk(chunk)

        new_actors = set()

        for pos, tile_types in chunk_data.items():
            for tile_type in tile_types:
                actor_name = f"{tile_type}_{pos[0]}_{pos[1]}"
                new_actor = None

                if tile_type == "grass_block":
                    new_actor = GrassBlock(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "grass":
                    new_actor = Grass(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "sand":
                    new_actor = Sand(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "log":
                    new_actor = Log(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "leaf":
                    new_actor = LeafBlock(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "dirt":
                    new_actor = Dirt(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "stone":
                    new_actor = Stone(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "coal":
                    new_actor = CoalOre(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "gold":
                    new_actor = GoldOre(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "iron":
                    new_actor = IronOre(actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "diamond":
                    new_actor = DiamondOre(actor_name, Vector(pos[0], pos[1]))

                if new_actor is not None:
                    new_actors.add(new_actor)

        if new_actors:
            self.level_ref.register_actor(new_actors)

