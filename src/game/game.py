from engine.game_base import *

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.datatypes import *
from components.material import Material
from components.character import Character
from components.background import *
from components.level import Level
#?ifdef CLIENT
from components.button import Button
from components.text import Text
from components.input_box import InputBox
from components.widget import Widget
from components.border import Border
#?endif
from collections import defaultdict

import random as r
import math
import noise
import os


CHUNK_SIZE = 32
ORIGINAL_CHUNK_SIZE = 8
DEVIDER = CHUNK_SIZE // ORIGINAL_CHUNK_SIZE
CAMERA_OFFSET_X = 1
CAMERA_OFFSET_Y = 1


class Log(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5),collidable=False, material = Material("res/textures/log.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(LogEntity(self.name, self.position))    

class Leaf(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), collidable=False, material = Material(Color(34, 139, 34)))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(LeafEntity(self.name, self.position))    

class Grass(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/grass_block.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(GrassEntity(self.name, self.position))

class Dirt(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/dirt.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(DirtEntity(self.name, self.position))
 
class Stone(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/stone.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(StoneEntity(self.name, self.position))        

class Coal(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/coal_ore.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(CoalEntity(self.name, self.position))    

class Iron(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/iron_ore.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(IronEntity(self.name, self.position))    

class Gold(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/gold_ore.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(GoldEntity(self.name, self.position))    

class DebugTunnel(Actor):
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.5, 0.5), collidable=False, material=Material(Color(255, 0, 0)))  # Bright red
        self.position = position

class TestPlayer(Character):
    def __init__(self, name, position):
        super().__init__(name, position=Vector(-5, 25), material = Material(Color(0, 0, 255)), jump_velocity=7)

class LogEntity(Rigidbody):
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(139, 69, 19)), restitution=0)   

class LeafEntity(Rigidbody):    
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(34, 139, 34)), restitution=0)             

class DirtEntity(Rigidbody):        
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(0, 255, 0)), restitution=0)

class GrassEntity(Rigidbody):        
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(255, 0, 0)), restitution=0)

class StoneEntity(Rigidbody):    
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(128, 128, 128)), restitution=0)

class CoalEntity(Rigidbody):    
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(0, 0, 0)), restitution=0)

class IronEntity(Rigidbody):    
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(192, 192, 192)), restitution=0)

class GoldEntity(Rigidbody):    
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.2, 0.2), collidable=True, material=Material(Color(255, 215, 0)), restitution=0)                                

        

#?ifdef CLIENT
#* This class was made by skelci
class WarningWidget:
    current_warnings = {}


    def __init__(self, name, text):
        self.widget = Border(name, Vector(1300, 10), Vector(290, 30), 2, Color(255, 0, 0), Color(30, 0, 0, 70), False, 2,
            subwidgets={
                "text": Text("text", Vector(0, 0), Vector(285, 20), Color(255, 255, 255), "res/fonts/arial.ttf", text=text)
            },
            subwidget_offsets={
                "text": Vector(5, 0)
            },
            subwidget_alignments={
                "text": Alignment.CENTER_LEFT,
            }
        )


    def show(self):
        if not self.widget.visible:
            self.widget.position.y = 10 + len(WarningWidget.current_warnings) * 50
            self.widget.visible = True
            WarningWidget.current_warnings[self.widget.name] = (self.widget, 15)
            return
        
        WarningWidget.current_warnings[self.widget.name] = (self.widget, 15)
        

    @classmethod
    def tick(cls, delta_time):
        widgets_to_remove = []
        for widget, time_left in cls.current_warnings.values():
            time_left -= delta_time
            cls.current_warnings[widget.name] = (widget, time_left)
            if time_left <= 0:
                widget.visible = False
                widgets_to_remove.append(widget.name)
                for widget, _ in cls.current_warnings.values():
                    widget.position.y -= 50

        for widget_name in widgets_to_remove:
            del cls.current_warnings[widget_name]



class ClientGame(ClientGameBase):
    def __init__(self):
        super().__init__()


        self.true_scroll = [0, 0]
        self.game_map = {}
        self.loaded_chunks = set()

        eng = self.engine

        eng.set_camera_width(16 * 2)
        eng.resolution = Vector(800, 600)

        # eng.fullscreen=True

        eng.show_all_stats()
        #eng.hide_all_stats()

        eng.add_actor_template(TestPlayer)
        eng.add_actor_template(Log)
        eng.add_actor_template(Leaf)
        eng.add_actor_template(Grass)
        eng.add_actor_template(Dirt)
        eng.add_actor_template(Stone)
        eng.add_actor_template(Coal)
        eng.add_actor_template(Iron)
        eng.add_actor_template(Gold)
        eng.add_actor_template(DebugTunnel)
        eng.add_actor_template(GrassEntity)
        eng.add_actor_template(DirtEntity)
        eng.add_actor_template(LogEntity)
        eng.add_actor_template(LeafEntity)
        eng.add_actor_template(StoneEntity)
        eng.add_actor_template(CoalEntity)
        eng.add_actor_template(IronEntity)
        eng.add_actor_template(GoldEntity)
    
        eng.register_background(Background("sky", (BackgroundLayer(Material(Color(100, 175, 255)), 20, 0.25), )))

        #* from here on, this method was made by skelci
        #?ifdef ENGINE
        eng.connect("localhost", 5555)
        #?endif

        self.switched_to_login_menu = False
        self.authenticated = False
        eng.register_background(Background("main_menu", (BackgroundLayer(Material(Color(19, 3, 31)), eng.camera_width, 0), )))
        eng.current_background = "main_menu"

        self.invalid_port_warning = WarningWidget("invalid_port_warning", "Invalid port number")
        self.failed_connection_warning = WarningWidget("failed_connection_warning", "Failed to connect to server")
        self.invalid_credentials_warning = WarningWidget("invalid_credentials_warning", "Invalid username or password")
        self.user_already_logged_in_warning = WarningWidget("user_already_logged_in_warning", "User is already logged in")
        self.username_already_exists_warning = WarningWidget("username_already_exists_warning", "Username already exists")
        self.wrong_credentials_warning = WarningWidget("wrong_credentials_warning", "Wrong username or password")
        eng.register_widget(self.invalid_port_warning.widget)
        eng.register_widget(self.failed_connection_warning.widget)
        eng.register_widget(self.invalid_credentials_warning.widget)
        eng.register_widget(self.user_already_logged_in_warning.widget)
        eng.register_widget(self.username_already_exists_warning.widget)
        eng.register_widget(self.wrong_credentials_warning.widget)

        def connect_to_server(server_address):
            if not server_address:
                return
            eng.widgets["main_menu-server_prompt"].subwidgets["prompt_field"].subwidgets["input_box"].current_text = ""
            server_address = server_address.split(":")
            server_ip = server_address[0]
            if len(server_address) == 1:
                port = 5555
            else:
                try:
                    port = int(server_address[1])
                except ValueError:
                    self.invalid_port_warning.show()
                    return
            try:
                eng.connect(server_ip, port)
            except Exception as e:
                print(f"Failed to connect: {e}")
                self.failed_connection_warning.show()
                return
            
        def get_usernname_password():
            username = self.engine.widgets["main_menu-credentials"].subwidgets["prompt_field-username"].subwidgets["input_box"].current_text
            password = self.engine.widgets["main_menu-credentials"].subwidgets["prompt_field-password"].subwidgets["input_box"].current_text
            return username, password
        
        def login():
            username, password = get_usernname_password()
            if not username or not password:
                self.invalid_credentials_warning.show()
                return
            self.engine.network.send("login", (username, password))

        def register():
            username, password = get_usernname_password()
            if not username or not password:
                self.invalid_credentials_warning.show()
                return
            self.engine.network.send("register", (username, password))

        def register_outcome(data):
            if data > 0:
                return
            elif data == -1:
                self.user_already_logged_in_warning.show()
            elif data == -2:
                self.username_already_exists_warning.show()
            elif data == -3:
                self.wrong_credentials_warning.show()

        eng.regisrer_network_command("register_outcome", register_outcome)

        class CredentialsInputBox(InputBox):
            def tick(self, delta_time, triggered_keys, pressed_keys, mouse_pos):
                super().tick(delta_time, triggered_keys, pressed_keys, mouse_pos)
                if self.is_in_focus:
                    if Keys.TAB in triggered_keys:
                        mmcs = eng.widgets["main_menu-credentials"].subwidgets
                        mmcs_username = mmcs["prompt_field-username"].subwidgets["input_box"]
                        mmcs_password = mmcs["prompt_field-password"].subwidgets["input_box"]
                        mmcs_username.is_in_focus = not mmcs_username.is_in_focus
                        mmcs_password.is_in_focus = not mmcs_password.is_in_focus
                        triggered_keys.remove(Keys.TAB)

        class PromptField(Border):
            def __init__(self, name, action = None):
                super().__init__(name, Vector(0, 0), Vector(500, 50), 0, Color(204, 255, 102), Color(255, 255, 153), True, 5,
                    subwidgets={
                        "input_box": CredentialsInputBox("input_box", Vector(0, 0), Vector(490, 40), Color(), "res/fonts/arial.ttf", 0, True, 22, action),
                    },
                    subwidget_offsets={
                        "input_box": Vector(7, -7),
                    },
                    subwidget_alignments={
                        "input_box": Alignment.CENTER_LEFT,
                    }
                )

        class PasswordInputBox(CredentialsInputBox):
            def tick(self, delta_time, triggered_keys, pressed_keys, mouse_pos):
                super().tick(delta_time, triggered_keys, pressed_keys, mouse_pos)
                cursor_char = "|" if self.is_cursor_visible else " "
                self.text = "*" * len(self.current_text[:self.cursor_position]) + cursor_char + "*" * len(self.current_text[self.cursor_position:])

        class PasswordField(PromptField):
            def __init__(self, name, action = None):
                super().__init__(name, action)
                self.subwidgets["input_box"] = PasswordInputBox("input_box", Vector(0, 0), Vector(490, 40), Color(), "res/fonts/arial.ttf", 0, True, 22, action)

        class PromptText(Text):
            def __init__(self, name, text):
                super().__init__(name, Vector(0, 0), Vector(500, 50), Color(255, 255, 255), "res/fonts/arial.ttf", 0, True, text)

        class PromptButton(Button):
            def __init__(self, name, text, action = None):
                super().__init__(name, Vector(0, 0), Vector(500, 75), 0, Color(192, 32, 224), Color(32, 4, 48), True, 5,
                    subwidgets={
                        "text": Text("text", Vector(0, 0), Vector(200, 40), Color(192, 32, 224), "res/fonts/arial.ttf", 0, True, text),
                    },
                    subwidget_offsets={
                        "text": Vector(0, 0),
                    },
                    subwidget_alignments={
                        "text": Alignment.CENTER,
                    },
                    hover_color = Color(0, 0, 0),
                    click_color = Color(64, 8, 96),
                    action = action
                )
        
        eng.register_widget(Widget("main_menu-server_prompt", Vector(), Vector(1600, 900), Color(0, 0, 0, 0), 0, True,
            subwidgets={
                "prompt_field": PromptField("prompt_field", connect_to_server),
                "prompt_text": PromptText("prompt_text", "Server Address:")
            },
            subwidget_offsets={
                "prompt_field": Vector(),
                "prompt_text": Vector(0, -53)
            },
            subwidget_alignments={
                "prompt_field": Alignment.CENTER,
                "prompt_text": Alignment.CENTER,
            }
        ))
        
        eng.register_widget(Widget("main_menu-credentials", Vector(), Vector(1600, 900), Color(0, 0, 0, 0), 0, False,
            subwidgets={
                "prompt_field-username": PromptField("prompt_field-username"),
                "prompt_text-username": PromptText("prompt_text-username", "Username:"),
                "prompt_field-password": PasswordField("prompt_field-password"),
                "prompt_text-password": PromptText("prompt_text-password", "Password:"),
                "prompt_button-login": PromptButton("prompt_button-login", "Login", login),
                "prompt_button-register": PromptButton("prompt_button-register", "Register", register),
            },
            subwidget_offsets={
                "prompt_field-username": Vector(200, -50),
                "prompt_text-username": Vector(-190, -52),
                "prompt_field-password": Vector(200, 10),
                "prompt_text-password": Vector(-185, 8),
                "prompt_button-login": Vector(0, 100),
                "prompt_button-register": Vector(0, 200),
            },
            subwidget_alignments={
                "prompt_field-username": Alignment.CENTER,
                "prompt_text-username": Alignment.CENTER,
                "prompt_field-password": Alignment.CENTER,
                "prompt_text-password": Alignment.CENTER,
                "prompt_button-login": Alignment.CENTER,
                "prompt_button-register": Alignment.CENTER,
            }
        ))


    #* this method was  made by skelci
    def handle_login(self):
        if self.engine.network and self.engine.network.connected and not self.switched_to_login_menu:
            self.switched_to_login_menu = True
            self.engine.widgets["main_menu-server_prompt"].visible = False
            self.engine.widgets["main_menu-credentials"].visible = True
            #?ifdef ENGINE
            self.engine.network.send("login", ("test", "test"))
            self.engine.network.send("register", ("test", "test"))
            #?endif
            return False

        if self.engine.check_network() and not self.authenticated:
            self.authenticated = True
            self.engine.widgets["main_menu-credentials"].visible = False
            self.engine.join_level("Test_Level")
            return True

        return self.engine.check_network()


    def tick(self):
        delta_time = super().tick()
        WarningWidget.tick(delta_time)
        if not self.handle_login():
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
    def __init__(self):
        super().__init__("Test_Level", TestPlayer, [], "sky")



#* This class was made by skelci
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


class TunnelGenerator:
    def __init__(self):
        self.width = 1.5
        self.curvature = 0.7# 0 = straight, 1 = very curved
        self.max_tunnel_length = 15
        

    def _center_point(self, region):
        """Calculate center of region"""
        avg_x = sum(p[0] for p in region) // len(region)
        avg_y = sum(p[1] for p in region) // len(region)
        return (avg_x, avg_y)
    
    def _distance(self, p1, p2):
        """Euclidean distance"""
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx*dx + dy*dy)
    

    def _dig_circle(self, cave_data, center_x, center_y, radius):
        """Carve out a circular tunnel area with validation"""
        tiles_dug = 0
        for y in range(int(center_y-radius), int(center_y+radius)+1):
            for x in range(int(center_x-radius), int(center_x+radius)+1):
                if (0 <= y < len(cave_data) and 
                    0 <= x < len(cave_data[0])):
                    dx = x - center_x
                    dy = y - center_y
                    if dx*dx + dy*dy <= radius*radius:
                        cave_data[y][x] = (cave_data[y][x][0], True, True)
                        tiles_dug += 1


    def _dig_line(self, cave_data, x1, y1, x2, y2):
        """Dig tunnel segment with varying width"""
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        for i in range(steps+1):
            t = i/max(steps, 1)
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            
            # Random width for organic look
            radius = self.width
            self._dig_circle(cave_data, x, y, radius)
    
    def _find_cave_regions(self, cave_data):
        # Implementation using flood fill
        regions = []
        visited = set()
        
        for y in range(len(cave_data)):
            for x in range(len(cave_data[0])):
                if (x,y) not in visited and cave_data[y][x][1]:
                    # New region found
                    region = []
                    stack = [(x,y)]
                    
                    while stack:
                        cx, cy = stack.pop()
                        if (cx,cy) in visited:
                            continue
                            
                        visited.add((cx,cy))
                        region.append((cx,cy))
                        
                        # Check neighbors
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < len(cave_data[0]) and \
                               (0 <= ny < len(cave_data)) and \
                               cave_data[ny][nx][1]:
                                stack.append((nx,ny))
                    
                    if len(region) >= 2:  # Minimum region size
                        regions.append(region)
        return regions
        
    
    def _connect_regions(self, cave_data, regions):
        centers = [self._center_point(region) for region in regions]
        # Connect each region to its nearest neighbor
        connected = set()
        connected.add(0)
        
        while len(connected) < len(regions):
            closest = None
            min_dist = float('inf')
            
            # Find closest unconnected region
            for i in connected:
                for j in range(len(regions)):
                    if j not in connected:
                        dist = self._distance(centers[i], centers[j])
                        if dist < min_dist:  # and dist < self.max_tunnel_length:
                            min_dist = dist
                            closest = (i, j)
            
            if closest:
                i, j = closest
                self._create_tunnel(cave_data, centers[i], centers[j])
                connected.add(j)
                

    def generate_tunnels(self, cave_data):
        # Find all cave regions
        regions = self._find_cave_regions(cave_data)
        
        if len(regions) < 2:
            return False
            
        # Connect regions with organic tunnels
        self._connect_regions(cave_data, regions)
        return True            

    
    def _calculate_curve(self, start, end):
        """Create smooth curve between points"""
        points = []
        steps = 10
        
        # Add midpoint with random offset
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Calculate perpendicular direction
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            perp_x = -dy/length
            perp_y = dx/length
            
            # Apply curvature
            offset = (r.random() * 2 - 1) * length * self.curvature
            mid_x += perp_x * offset
            mid_y += perp_y * offset
        
        # Generate bezier curve points
        for i in range(steps+1):
            t = i/steps
            # Quadratic bezier
            x = (1-t)**2 * start[0] + 2*(1-t)*t * mid_x + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * mid_y + t**2 * end[1]
            points.append((int(x), int(y)))
        return points
    

    def _create_tunnel(self, cave_data, start, end):
        # Create curved path
        path = self._calculate_curve(start, end)
        
        # Dig along path
        for i in range(len(path)-1):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            self._dig_line(cave_data, x1, y1, x2, y2)


class ServerGame(ServerGameBase):
    def __init__(self):
        super().__init__()
        self.engine.max_tps = 60
        self.engine.start_network("0.0.0.0", 5555, 10)

        self.engine.register_level(TestLevel())

        self.engine.register_key(Keys.W, KeyPressType.HOLD, KeyHandler.key_W)
        self.engine.register_key(Keys.A, KeyPressType.HOLD, KeyHandler.key_A)
        self.engine.register_key(Keys.D, KeyPressType.HOLD, KeyHandler.key_D)
        self.engine.register_key(Keys.MOUSE_LEFT, KeyPressType.TRIGGER, breaking_blocks)
        self.game_map = {}
        self.loaded_chunks = set()
        self.current_base_chunk = Vector(0, 0)
        self.tunnel_generator = TunnelGenerator()
    

        #?ifdef ENGINE
        self.engine.console.handle_cmd("build_server")
        self.engine.console.handle_cmd("build_client")
        #?endif


    @staticmethod
    def smoothstep(val, edge0, edge1):
        t = max(0.0, min((val - edge0) / (edge1 - edge0), 1.0))
        return t * t * (3 - 2 * t)


    def generate_chunk(self, x, y):
        chunk_data = []
        chunk_origin = Vector(x, y) * CHUNK_SIZE
        tree_threshold = 0.03
        
        # Noise parameters
        terrain_scale = 0.035
        cave_scale_x = 0.02
        cave_scale_y = 0.025
        surface_threshold = 0.6
        mid_threshold = 0.5      
        deep_threshold = 0.34  
        cave_octaves = 2
        cave_persistence = 0.5
        
        # Enhanced ore generation parameters - different for each type
        ore_parameters = {
            "coal": {
                "scale": 0.05,       # Larger scale = bigger, spread-out veins
                "threshold": 0.72,   # Lower threshold = more common
                "base": 1000,        # Unique noise pattern
                "min_depth": 5,      # Shallowest depth
                "vein_size": (2, 4), # Larger veins (now represents potential blocks)
                "spread": 1,         # Wider spread
                "density": 0.8     # Higher density
            },
            "iron": {
                "scale": 0.04,
                "threshold": 0.76,
                "base": 2000,
                "min_depth": 10,
                "vein_size": (2, 3),
                "spread": 1,
                "density": 0.75
            },
            "gold": {
                "scale": 0.03,       # Smaller scale = tighter veins
                "threshold": 0.8,    # Slightly higher threshold = slightly rarer
                "base": 3000,
                "min_depth": 10,
                "vein_size": (1, 2),  # Smaller veins
                "spread": 1,          # Tighter clusters
                "density": 0.7
            }
        }
        
        # First calculate ground levels
        ground_levels = []
        for x_pos in range(CHUNK_SIZE):
            pos_x = chunk_origin.x + x_pos
            height_noise = noise.pnoise1(pos_x * terrain_scale, repeat=9999999, base=0)
            ground_levels.append(16 - math.floor(height_noise * 10))
        
        # Generate initial noise data
        noise_data = []
        for y_pos in range(CHUNK_SIZE):
            row = []
            for x_pos in range(CHUNK_SIZE):
                pos = chunk_origin + Vector(x_pos, y_pos)
                ground_level = ground_levels[x_pos]
                
                # Cave generation
                base_val = noise.snoise2(
                    pos.x * cave_scale_x,
                    pos.y * cave_scale_y,
                    octaves=cave_octaves,
                    persistence=cave_persistence,
                    lacunarity=2.0
                )
                combined_noise = base_val + (noise.snoise2(
                    pos.x * cave_scale_x * 3,
                    pos.y * cave_scale_y * 3,
                    octaves=1
                ) * 0.2)
                
                # Depth-based thresholds
                depth = ground_level - pos.y
                if depth < 6:
                    effective_threshold = surface_threshold
                elif 6 <= depth < 16:
                    effective_threshold = surface_threshold - (surface_threshold - mid_threshold) * self.smoothstep(depth, 6, 16)
                elif 16 <= depth < 30:
                    effective_threshold = mid_threshold - (mid_threshold - deep_threshold) * self.smoothstep(depth, 16, 30)
                else:
                    effective_threshold = deep_threshold

                is_cave = combined_noise > effective_threshold and pos.y < ground_level
                row.append((pos, is_cave, False))
            noise_data.append(row)
        
        # Generate tunnels
        if y <= 0:
            tunnel_gen = TunnelGenerator()
            if tunnel_gen.generate_tunnels(noise_data):
                for y_pos in range(CHUNK_SIZE):
                    for x_pos in range(CHUNK_SIZE):
                        pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                        if is_tunnel:
                            chunk_data.append([(pos.x, pos.y), None])
        
        # Generate ore veins with flood-fill approach for better connectivity
        ore_positions = set()
        for ore_type, parameters in ore_parameters.items():
            # First pass - find potential vein starts
            potential_starts = []
            for y_pos in range(CHUNK_SIZE):
                for x_pos in range(CHUNK_SIZE):
                    pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                    ground_level = ground_levels[x_pos]
                    depth = ground_level - pos.y
                    
                    if (not is_cave and not is_tunnel and 
                        depth > parameters["min_depth"] and 
                        (pos.x, pos.y) not in ore_positions):
                        
                        ore_noise = noise.snoise2(
                            pos.x * parameters["scale"],
                            pos.y * parameters["scale"],
                            octaves=2,
                            persistence=0.5,
                            lacunarity=2.0,
                            base=parameters["base"]
                        )
                        
                        if ore_noise > parameters["threshold"]:
                            potential_starts.append((x_pos, y_pos))
            
            # Second pass - generate connected veins from starts
            for start_x, start_y in potential_starts:
                if (chunk_origin.x + start_x, chunk_origin.y + start_y) in ore_positions:
                    continue
                    
                min_vein, max_vein = parameters["vein_size"]
                target_size = r.randint(min_vein, max_vein)
                current_size = 0
                queue = []
                visited = set()
                
                start_pos = chunk_origin + Vector(start_x, start_y)
                queue.append((start_x, start_y))
                visited.add((start_x, start_y))
                
                while queue and current_size < target_size:
                    x_pos, y_pos = queue.pop(0)
                    pos = chunk_origin + Vector(x_pos, y_pos)
                    
                    # Only place ore if it meets conditions
                    ground_level = ground_levels[x_pos]
                    depth = ground_level - pos.y
                    if (not noise_data[y_pos][x_pos][1] and  # Not a cave
                        not noise_data[y_pos][x_pos][2] and  # Not a tunnel
                        depth > parameters["min_depth"] and
                        (pos.x, pos.y) not in ore_positions and
                        r.random() < parameters["density"]):
                        
                        chunk_data.append([(pos.x, pos.y), ore_type])
                        ore_positions.add((pos.x, pos.y))
                        current_size += 1
                    
                    # Add neighbors to queue if they're good candidates
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx, ny = x_pos + dx, y_pos + dy
                        if (0 <= nx < CHUNK_SIZE and 0 <= ny < CHUNK_SIZE and
                            (nx, ny) not in visited):
                            
                            # Check if neighbor has good ore potential
                            n_pos = chunk_origin + Vector(nx, ny)
                            n_ground_level = ground_levels[nx]
                            n_depth = n_ground_level - n_pos.y
                            
                            if (n_depth > parameters["min_depth"] and
                                not noise_data[ny][nx][1] and
                                not noise_data[ny][nx][2]):
                                
                                n_ore_noise = noise.snoise2(
                                    n_pos.x * parameters["scale"],
                                    n_pos.y * parameters["scale"],
                                    octaves=2,
                                    persistence=0.5,
                                    lacunarity=2.0,
                                    base=parameters["base"]
                                )
                                
                                if n_ore_noise > parameters["threshold"] * 0.8:  # Slightly lower threshold for neighbors
                                    visited.add((nx, ny))
                                    queue.append((nx, ny))
        
        # Rest of terrain generation (unchanged)
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
                pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                ground_level = ground_levels[x_pos]
                
                if any(block[0] == (pos.x, pos.y) for block in chunk_data):
                    continue
                    
                if is_cave:
                    continue
                elif pos.y == ground_level:
                    chunk_data.append([(pos.x, pos.y), "grass"])
                    if r.random() < tree_threshold:
                        tree_height = r.randint(4, 7)
                        top = pos + Vector(0, tree_height)
                        for h in range(1, tree_height + 1):
                            trunk_pos = pos + Vector(0, h)
                            if trunk_pos.y >= chunk_origin.y:
                                chunk_data.append([(trunk_pos.x, trunk_pos.y), "log"])
                        rx = 3.25
                        ry = 4.5
                        top_leaf_pos = top + Vector(0, 5)
                        bottom_leaf_pos = top + Vector(0, 0)
                        chunk_data.append([(top_leaf_pos.x, top_leaf_pos.y), "leaf"])
                        chunk_data.append([(bottom_leaf_pos.x, bottom_leaf_pos.y), "leaf"])
                        for dy in range(0, int(ry) + 1):
                            for dx in range(-int(rx), int(rx) + 1):
                                if (dx*dx)/(rx*rx) + (dy*dy)/(ry*ry) <= 1:
                                    leaf_pos = top + Vector(dx, dy)
                                    chunk_data.append([(leaf_pos.x, leaf_pos.y), "leaf"])
                elif pos.y < ground_level and pos.y > ground_level - 5:
                    chunk_data.append([(pos.x, pos.y), "dirt"])
                elif pos.y <= ground_level - 5:
                    chunk_data.append([(pos.x, pos.y), "stone"])
        
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
        ud = (ud // DEVIDER) + 1
        for offset_y in range(-ud - 2, ud + 3):
            for offset_x in range(-ud - 2, ud + 3):
                chunks_to_load.append((
                    base_chunk_vector.x + offset_x, 
                    base_chunk_vector.y + offset_y
                ))

        for base_chunk_x, base_chunk_y in chunks_to_load:
            self.generate_and_load_chunks(base_chunk_x, base_chunk_y)


def breaking_blocks(engine_ref, level_ref, id):
    #print('breaking_blocks')
    # Get the player's position
    player = level_ref.actors[engine_ref.get_player_actor(id)].position
    #chunk_x, chunk_y=engine_ref.players[id].previous_chunk.rounded

    function_3x3=level_ref.get_actors_in_chunks_3x3(get_chunk_cords(player))
    #print(function_3x3)

    # Get the chunk name and position
    #chunk_Actor_name=tuple(engine_ref.levels["Test_Level"].chunks[chunk_x][chunk_y])

    # Get the positions of actors in the current chunk


    #Get the mouse position 
    mouse_pos = engine_ref.players[id].world_mouse_pos
    mouse_pos = mouse_pos.rounded
    #print(mouse_pos)   

    #allowed to break this blocks
    allowed_blocks=tuple(("grass", "dirt", "stone", "log", "leaves", "Leaves", "LEAVES", "leaf", "Leaf", "LEAF", "Coal", "Iron", "Gold"))

    for actor in function_3x3:
        #actor=engine_ref.levels["Test_Level"].actors[actor_name]
        #print(actor_name)
        actor_position = actor.position.rounded
        #print(actor_position)

        if actor_position == mouse_pos:
            #print('actor:'+actor_position)
            if actor.name.startswith("__Player_"):
                break
            #if 
            engine_ref.levels["Test_Level"].destroy_actor(actor)          
            break
            

