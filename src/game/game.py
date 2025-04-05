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
import os


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

class DebugTunnel(Actor):
    def __init__(self, engine_ref, name, position):
        super().__init__(engine_ref, name, position=position, 
                        half_size=Vector(0.5, 0.5), 
                        collidable=False, 
                        material=Material(Color(255, 0, 0)))  # Bright red
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

        eng.set_camera_width(16 * 16)
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
        eng.add_actor_template(DebugTunnel)
    
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
        self.current_base_chunk = Vector(0, 0)
    


    @staticmethod
    def smoothstep(val, edge0, edge1):
        t = max(0.0, min((val - edge0) / (edge1 - edge0), 1.0))
        return t * t * (3 - 2 * t)
    


    def dig_tunnel_segment(self, cave_data, x1, y1, x2, y2, min_width, max_width):
        """Digs a straight tunnel segment with varying width"""
        # Calculate steps needed
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        # Ensure we have at least 1 step to avoid division by zero
        steps = max(steps, 1)
        
        for t in range(steps + 1):
            # Calculate current position along the line
            t_normalized = t / steps
            bx = round(x1 + dx * t_normalized)
            by = round(y1 + dy * t_normalized)
            
            # Vary width along the tunnel
            current_width = r.randint(min_width, max_width)
            
            # Carve out the tunnel area
            for wy in range(-current_width, current_width + 1):
                for wx in range(-current_width, current_width + 1):
                    # Circular carving pattern
                    if wx**2 + wy**2 <= current_width**2 + 1:  # +1 for smoother edges
                        nx, ny = bx + wx, by + wy
                        if 0 <= nx < len(cave_data[0]) and 0 <= ny < len(cave_data):
                            cave_data[ny][nx] = (cave_data[ny][nx][0], True, True)  # Mark as tunnel



    def find_cave_regions(self, cave_data):
        """Find only noise-generated cave regions (ignoring tunnels)"""
        regions = []
        height = len(cave_data)
        if height == 0:
            return regions
        width = len(cave_data[0])
        
        visited = [[False for _ in range(width)] for _ in range(height)]
        
        for y in range(height):
            for x in range(width):
                # Only look for natural caves (is_cave=True, is_tunnel=False)
                if (not visited[y][x] and 
                    cave_data[y][x][1] and  # is_cave
                    not cave_data[y][x][2]):  # not is_tunnel
                    
                    region = []
                    stack = [(x, y)]
                    visited[y][x] = True
                    
                    while stack:
                        cx, cy = stack.pop()
                        region.append((cx, cy))
                        
                        # 4-directional connectivity for more natural cave shapes
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = cx + dx, cy + dy
                            if (0 <= nx < width and 0 <= ny < height and
                                not visited[ny][nx] and 
                                cave_data[ny][nx][1] and 
                                not cave_data[ny][nx][2]):
                                visited[ny][nx] = True
                                stack.append((nx, ny))
                    
                    # Minimum 3 blocks to be considered a cave
                    if len(region) >= 3:
                        regions.append(region)
        
        return regions

    def connect_cave_regions(self, cave_data):
        """Connect only noise-generated cave regions"""
        regions = self.find_cave_regions(cave_data)
        if len(regions) < 2:
            return  # No tunnels if less than 2 caves
        
        # Calculate center points of each cave
        centers = []
        for region in regions:
            avg_x = sum(x for x,y in region) // len(region)
            avg_y = sum(y for x,y in region) // len(region)
            centers.append((avg_x, avg_y))
        
        # Connect each cave to its nearest neighbor
        connected = set([0])  # Start with first cave
        while len(connected) < len(regions):
            closest_pair = None
            min_distance = float('inf')
            
            # Find closest unconnected cave to any connected cave
            for i in connected:
                for j in range(len(regions)):
                    if j not in connected:
                        dist = (centers[i][0]-centers[j][0])**2 + (centers[i][1]-centers[j][1])**2
                        if dist < min_distance:
                            min_distance = dist
                            closest_pair = (i, j)
            
            if closest_pair:
                i, j = closest_pair
                # Create tunnel between these caves
                self.dig_organic_tunnel(
                    cave_data,
                    centers[i][0], centers[i][1],
                    centers[j][0], centers[j][1],
                    min_width=1,  # Narrower tunnels
                    max_width=2
                )
                connected.add(j)
    

    def dig_organic_tunnel(self, cave_data, x1, y1, x2, y2, min_width=1, max_width=2):
        """Create natural-looking tunnels between cave centers"""
        # Calculate direction
        dx, dy = x2 - x1, y2 - y1
        distance = max(abs(dx), abs(dy))
        
        # Simple curved path with 1 control point
        mid_x = x1 + dx//2 + r.randint(-1, 1)
        mid_y = y1 + dy//2 + r.randint(-1, 1)
        
        # Dig the tunnel segments
        self.dig_tunnel_segment(cave_data, x1, y1, mid_x, mid_y, min_width, max_width)
        self.dig_tunnel_segment(cave_data, mid_x, mid_y, x2, y2, min_width, max_width)
        
        # Only add branches for longer tunnels
        if distance > 6 and r.random() < 0.3:
            branch_x = mid_x + r.randint(-2, 2)
            branch_y = mid_y + r.randint(-2, 2)
            self.dig_tunnel_segment(cave_data, mid_x, mid_y, branch_x, branch_y, 
                                max(1, min_width-1), max_width)
        


    def dig_tunnel_segment(self, cave_data, x1, y1, x2, y2, min_width, max_width):
        """Digs a straight tunnel segment with varying width"""
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        for i in range(steps + 1):
            t = i / max(steps, 1)
            bx = round(x1 + dx * t)
            by = round(y1 + dy * t)
            
            # Vary width along the tunnel
            current_width = r.randint(min_width, max_width)
            
            # Carve out the tunnel area
            for wy in range(-current_width, current_width + 1):
                for wx in range(-current_width, current_width + 1):
                    if wx**2 + wy**2 <= current_width**2 + 1:  # Circular pattern
                        nx, ny = bx + wx, by + wy
                        if 0 <= ny < len(cave_data) and 0 <= nx < len(cave_data[0]):
                            # Mark as tunnel (preserving original noise value)
                            cave_data[ny][nx] = (cave_data[ny][nx][0], True, True)
        


    def create_guaranteed_tunnel(self, cave_data, x1, y1, x2, y2, min_width=2, max_width=3):
        """Creates an organic-looking tunnel between two points"""
        # Add some jitter to make the tunnel path more natural
        mid_x = (x1 + x2) // 2 + r.randint(-3, 3)
        mid_y = (y1 + y2) // 2 + r.randint(-3, 3)
        
        # Dig first segment
        self.dig_tunnel_segment(cave_data, x1, y1, mid_x, mid_y, min_width, max_width)
        
        # Dig second segment
        self.dig_tunnel_segment(cave_data, mid_x, mid_y, x2, y2, min_width, max_width)
        
        # 40% chance to add a small side branch
        if r.random() < 0.4:
            branch_x = mid_x + r.randint(-4, 4)
            branch_y = mid_y + r.randint(-4, 4)
            self.dig_tunnel_segment(
                cave_data, 
                mid_x, mid_y, 
                branch_x, branch_y,
                max(1, min_width-1),  # Slightly narrower branch
                max(2, max_width-1)
            )

    

    def create_tunnel_between(self, cave_data, x1, y1, x2, y2, base_width=3):
        """Create organic tunnel between two points with width variation"""
        if x1 == x2 and y1 == y2:
            return
        
        # Add some jitter to the path
        mid_x = (x1 + x2) // 2 + r.randint(-3, 3)
        mid_y = (y1 + y2) // 2 + r.randint(-3, 3)
        
        # Create two curved segments
        self.dig_tunnel_segment(cave_data, x1, y1, mid_x, mid_y, base_width)
        self.dig_tunnel_segment(cave_data, mid_x, mid_y, x2, y2, base_width)
        
        # 30% chance to add a small side tunnel
        if r.random() < 0.3:
            branch_x = mid_x + r.randint(-4, 4)
            branch_y = mid_y + r.randint(-4, 4)
            self.dig_tunnel_segment(cave_data, mid_x, mid_y, branch_x, branch_y, max(1, base_width-1))
                                    

    def generate_chunk(self, x, y):
        chunk_data = []
        chunk_origin = Vector(x, y) * CHUNK_SIZE
        tree_threshold = 0.1
        
        # Your original unchanged noise parameters
        terrain_scale = 0.035
        cave_scale_x = 0.02
        cave_scale_y = 0.025
        surface_threshold = 0.6
        mid_threshold = 0.5      
        deep_threshold = 0.34  
        cave_octaves = 2
        cave_persistence = 0.5
        
        # Generate initial cave data as (position, is_cave, is_tunnel) tuples
        noise_data = []
        for y_pos in range(CHUNK_SIZE):
            row = []
            for x_pos in range(CHUNK_SIZE):
                pos = chunk_origin + Vector(x_pos, y_pos)
                
                # Terrain height (unchanged)
                height_noise = noise.pnoise1(pos.x * terrain_scale, repeat=9999999, base=0)
                height_val = math.floor(height_noise * 10)
                ground_level = 16 - height_val
                
                # Cave generation (unchanged noise calculation)
                base_val = noise.snoise2(
                    pos.x * cave_scale_x,
                    pos.y * cave_scale_y,
                    octaves=cave_octaves,
                    persistence=cave_persistence,
                    lacunarity=2.0
                )
                detail = noise.snoise2(
                    pos.x * cave_scale_x * 3,
                    pos.y * cave_scale_y * 3,
                    octaves=1
                ) * 0.2
                combined_noise = base_val + detail
                
                # Depth thresholds (unchanged)
                depth = ground_level - pos.y
                if depth < 6:
                    effective_threshold = surface_threshold
                elif depth >= 6 and depth < 16:
                    effective_threshold = surface_threshold - (surface_threshold - mid_threshold) * self.smoothstep(depth, 6, 16)
                elif depth >= 16 and depth < 30:
                    effective_threshold = mid_threshold - (mid_threshold - deep_threshold) * self.smoothstep(depth, 16, 30)
                else:
                    effective_threshold = deep_threshold

                row.append((pos, combined_noise > effective_threshold, False))
            noise_data.append(row)
        
        # NEW: Improved cave connection system
        regions = []
        visited = [[False for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        
        # Find all cave regions (4-way connectivity)
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                if (not visited[y_pos][x_pos] and 
                    noise_data[y_pos][x_pos][1] and  # is_cave
                    not noise_data[y_pos][x_pos][2]):  # not already tunnel
                    
                    # Flood fill to find connected cave region
                    region = []
                    stack = [(x_pos, y_pos)]
                    visited[y_pos][x_pos] = True
                    
                    while stack:
                        cx, cy = stack.pop()
                        region.append((cx, cy))
                        
                        # Check 4-directional neighbors
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = cx + dx, cy + dy
                            if (0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and
                                not visited[ny][nx] and 
                                noise_data[ny][nx][1] and 
                                not noise_data[ny][nx][2]):
                                visited[ny][nx] = True
                                stack.append((nx, ny))
                    
                    if len(region) >= 3:  # Minimum 3 blocks to count as a cave
                        regions.append(region)
        
        # Connect the two closest cave regions if found
        if len(regions) >= 2:
            # Find two closest caves
            min_dist = float('inf')
            best_pair = None
            
            for i in range(len(regions)):
                for j in range(i+1, len(regions)):
                    # Get approximate centers
                    x1 = sum(p[0] for p in regions[i]) // len(regions[i])
                    y1 = sum(p[1] for p in regions[i]) // len(regions[i])
                    x2 = sum(p[0] for p in regions[j]) // len(regions[j])
                    y2 = sum(p[1] for p in regions[j]) // len(regions[j])
                    
                    dist = (x2-x1)**2 + (y2-y1)**2
                    if dist < min_dist:
                        min_dist = dist
                        best_pair = (x1, y1, x2, y2)
            
            if best_pair:
                x1, y1, x2, y2 = best_pair
                # Create winding tunnel between them
                mid_x = (x1 + x2) // 2 + r.randint(-1, 1)
                mid_y = (y1 + y2) // 2 + r.randint(-1, 1)
                
                # Mark tunnel segments
                for t in [0.0, 0.33, 0.66, 1.0]:  # Smooth path with 3 segments
                    bx = int(x1 + (x2-x1)*t)
                    by = int(y1 + (y2-y1)*t)
                    radius = r.randint(1, 2)
                    # Mark circular area around path
                    for dy in range(-radius, radius+1):
                        for dx in range(-radius, radius+1):
                            if dx*dx + dy*dy <= radius*radius + 1:  # Circular shape
                                nx, ny = bx + dx, by + dy
                                if (0 <= nx < CHUNK_SIZE and 
                                    0 <= ny < CHUNK_SIZE):
                                    pos, is_cave, _ = noise_data[ny][nx]
                                    noise_data[ny][nx] = (pos, is_cave, True)  # Mark as tunnel
        
        # Convert to final tiles
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                
                # Tunnels take priority (visualization)
                if is_tunnel:
                    chunk_data.append([(pos.x, pos.y), "tunnel_debug"])
                    continue
                    
                # Leave natural caves empty
                if is_cave:
                    continue
                    
                # Generate terrain (unchanged from your original)
                height_noise = noise.pnoise1(pos.x * terrain_scale, repeat=9999999, base=0)
                height_val = math.floor(height_noise * 10)
                ground_level = 16 - height_val
                
                tile_type = None
                if pos.y == ground_level:
                    tile_type = "grass"
                    if r.random() < tree_threshold:
                        tree_height = r.randint(4, 7)
                        for h in range(1, tree_height + 1):
                            trunk_pos = pos + Vector(0, h)
                            if trunk_pos.y >= chunk_origin.y:
                                chunk_data.append([(trunk_pos.x, trunk_pos.y), "log"])
                elif pos.y < ground_level and pos.y > ground_level - 5:
                    tile_type = "dirt"
                elif pos.y <= ground_level - 5:
                    tile_type = "stone"
                    if pos.y <= ground_level - 10 and r.random() < 0.02:
                        tile_type = "coal"
                    if pos.y <= ground_level - 20 and r.random() < 0.01:
                        tile_type = "iron"
                    if pos.y <= ground_level - 35 and r.random() < 0.005:
                        tile_type = "gold"

                if tile_type is not None:
                    chunk_data.append([(pos.x, pos.y), tile_type])
        
        return chunk_data
        

    def generate_and_load_chunks(self, chunk_x, chunk_y):
        level = self.engine.levels.get("Test_Level")
        if level is None:
            return

        target_chunk = f"{chunk_x};{chunk_y}"
        
        # Generate this chunk and immediate neighbors
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = chunk_x + dx, chunk_y + dy
                neighbor_chunk = f"{nx};{ny}"
                if neighbor_chunk not in self.game_map:
                    self.game_map[neighbor_chunk] = self.generate_chunk(nx, ny)
        
        # Load the chunk if not already loaded
        if target_chunk not in self.loaded_chunks:
            actors_to_add = []
            for tile in self.game_map.get(target_chunk, []):
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
                elif tile_type == "iron":
                    new_actor = Iron(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "gold":
                    new_actor = Gold(self.engine, actor_name, Vector(pos[0], pos[1]))
                elif tile_type == "tunnel_debug":
                    new_actor = DebugTunnel(self.engine, actor_name, Vector(pos[0], pos[1]))
                
                if new_actor is not None:
                    actors_to_add.append(new_actor)

            # Register all actors at once
            for actor in actors_to_add:
                level.register_actor(actor)
            
            self.loaded_chunks.add(target_chunk)



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
        
        # Calculate average position
        avg_x = sum(p.x for p in positions) / len(positions)
        avg_y = sum(p.y for p in positions) / len(positions)
        avg_pos = Vector(avg_x, avg_y)

        # Calculate new base chunk with smoothing
        new_base_chunk = Vector(
            math.floor((avg_pos.x + CHUNK_SIZE/2) / CHUNK_SIZE),
            math.floor((avg_pos.y + CHUNK_SIZE/2) / CHUNK_SIZE)
        )
        
        if not hasattr(self, "current_base_chunk"):
            self.current_base_chunk = new_base_chunk
        else:
            smoothing_factor = 0.5
            self.current_base_chunk += (new_base_chunk - self.current_base_chunk) * smoothing_factor

        base_chunk_vector = self.current_base_chunk.floored
        
        # Load chunks in radius
        chunks_to_load = []
        ud = 0
        if self.engine.players:
            for player in self.engine.players.values():
                ud += player.update_distance
        ud //= len(self.engine.players)
        for offset_y in range(-ud, ud + 1):
            for offset_x in range(-ud, ud + 1):
                chunks_to_load.append((
                    base_chunk_vector.x + offset_x, 
                    base_chunk_vector.y + offset_y
                ))

        for base_chunk_x, base_chunk_y in chunks_to_load:
            self.generate_and_load_chunks(base_chunk_x, base_chunk_y)