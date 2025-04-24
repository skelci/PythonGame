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

import threading
import random as r
import math
import noise
import os
import random


ORIGINAL_CHUNK_SIZE = CHUNK_SIZE
CHUNK_SIZE = 32
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
        r=random.randint(3,5)
        for i in range(r):
            self.level_ref.register_actor(LogEntity(self.name, self.position))    
            #print('wood iz log')

class Leaf(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), collidable=False, material = Material("res/textures/leaf_block.png"), render_layer=1)
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        r=random.randint(0,5)
        #print(r)
        for i in range(r):
            self.level_ref.register_actor(StickEntity(self.name, self.position))
            #print("stick iz leaf") 
        for j in range(8):
            self.level_ref.register_actor(LeafEntity(self.name, self.position))
            #print("leaves:", j) 

class Grass(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/grass_block.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        for i in range(4):
            self.level_ref.register_actor(DirtEntity(self.name, self.position))
            #print("entity dirt iz grasa")

class Dirt(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/dirt.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        r=random.randint(3,5)
        for i in range(r):
            self.level_ref.register_actor(DirtEntity(self.name, self.position))
            #print('dirt iz dirta')
        chance=random.randint(1,4)
        if chance==1:
            self.level_ref.register_actor(StoneEntity(self.name, self.position))
            #print('stone iz dirta')    
 
class Stone(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/stone.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        r=random.randint(3,5)
        for i in range(r):
            self.level_ref.register_actor(StoneEntity(self.name, self.position))   
            #print('rock iz stone')     

class Coal(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/coal_ore.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        self.level_ref.register_actor(CoalEntity(self.name, self.position))  
        r=random.randint(1,2)
        for i in range(2):
            self.level_ref.register_actor(StoneEntity(self.name, self.position))  
            #print("rock iz coala")
        if r==1:
             self.level_ref.register_actor(StoneEntity(self.name, self.position))   

class Iron(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/iron_ore.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        for i in range(3):
            self.level_ref.register_actor(IronEntity(self.name, self.position))   
        r=random.randint(1,2)
        for i in range(2):
            self.level_ref.register_actor(StoneEntity(self.name, self.position))  
            #print("rock iz irona") 
        if r==1:
            self.level_ref.register_actor(StoneEntity(self.name, self.posiiton))    

class Gold(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/gold_ore.png"))
        self.position = position
    def __del__(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        for i in range(3):
            self.level_ref.register_actor(GoldEntity(self.name, self.position)) 
        r=random.randint(1,2)
        for i in range(2):
            self.level_ref.register_actor(StoneEntity(self.name, self.position))  
            #print("rock iz golda")
        if r==1:
            self.level_ref.register_actor(StoneEntity(self.name, self.position))    

class DebugTunnel(Actor):
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.5, 0.5), collidable=False, material=Material(Color(255, 0, 0)), render_layer=1)  # Bright red
        self.position = position

class TestPlayer(Character):
    def __init__(self, name, position):
        super().__init__(name, position=Vector(-5, 27), material = Material(Color(0, 0, 255)), jump_velocity=7, render_layer=2)

class LogEntity(Rigidbody):
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y) 
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/log_entity.png"), restitution=0, initial_velocity=Initial_velocity)   

class StickEntity(Rigidbody):    
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material(Color(145, 69, 34)), restitution=0, initial_velocity=Initial_velocity)             

class DirtEntity(Rigidbody):        
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/dirt_entity.png"), restitution=0, initial_velocity=Initial_velocity)

class GrassEntity(Rigidbody):        
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material(Color(255, 0, 0)), restitution=0, initial_velocity=Initial_velocity)

class StoneEntity(Rigidbody):    
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/stone_entity.png"), restitution=0, initial_velocity=Initial_velocity)

class CoalEntity(Rigidbody):    
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/coal_ore_entity.png"), restitution=0, initial_velocity=Initial_velocity)

class IronEntity(Rigidbody):    
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/iron_ore_entity.png"), restitution=0, initial_velocity=Initial_velocity)

class GoldEntity(Rigidbody):    
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/gold_ore_entity.png"), restitution=0, initial_velocity=Initial_velocity)

class LeafEntity(Rigidbody):
    def __init__(self, name, position):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material(Color(0, 215, 0)), restitution=0, initial_velocity=Initial_velocity)                                

        

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

        eng.set_camera_width(16 * 3)
        eng.resolution = Vector(1600, 900)

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
        eng.add_actor_template(StickEntity)
        eng.add_actor_template(StoneEntity)
        eng.add_actor_template(CoalEntity)
        eng.add_actor_template(IronEntity)
        eng.add_actor_template(GoldEntity)
        eng.add_actor_template(LeafEntity)
    
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

    @staticmethod
    def key_C(engine_ref, level_ref,id):
        # Spawn a CoalEntity at the player's position
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


class TunnelGenerator:
    def __init__(self):
        self.width = 1.5
        self.curvature = 0.6# 0 = straight, 1 = very curved
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
        

        self.engine.register_level(TestLevel())

        self.engine.register_key(Keys.W, KeyPressType.HOLD, KeyHandler.key_W)
        self.engine.register_key(Keys.A, KeyPressType.HOLD, KeyHandler.key_A)
        self.engine.register_key(Keys.D, KeyPressType.HOLD, KeyHandler.key_D)
        self.engine.register_key(Keys.C, KeyPressType.TRIGGER, KeyHandler.key_C)
        self.engine.register_key(Keys.MOUSE_LEFT, KeyPressType.TRIGGER, breaking_blocks)
        self.game_map = set()
        self.current_base_chunk = Vector(0, 0)
        self.tunnel_generator = TunnelGenerator()
    

        #?ifdef ENGINE
        self.engine.console.handle_cmd("build_server")
        self.engine.console.handle_cmd("build_client")
        #?endif


        self.generate_and_load_chunks(-1, 0)

        self.engine.start_network("0.0.0.0", 5555, 10)

    @staticmethod
    def smoothstep(val, edge0, edge1):
        t = max(0.0, min((val - edge0) / (edge1 - edge0), 1.0))
        return t * t * (3 - 2 * t)
    

    @staticmethod
    def tree_generation(chunk_origin, ground_level, pos, tree_threshold, shared_tree_positions, chunk_data):
        start_pos = chunk_origin + Vector(pos.x, pos.y)
        
        if r.random() > tree_threshold and start_pos.y == ground_level:  
            can_spawn = True
            for tree_pos in shared_tree_positions:
                if abs(tree_pos.x - pos.x) < 4 and abs(tree_pos.y - pos.y) < 4:
                    can_spawn = False
                    break
               
            if can_spawn:
                shared_tree_positions.append(pos)
                tree_height = r.randint(4, 7)
                top = pos + Vector(0, tree_height)
                # Add trunk
                for h in range(1, tree_height + 1):
                    trunk_pos = pos + Vector(0, h)
                    if trunk_pos.y >= chunk_origin.y:
                        chunk_data.append(((trunk_pos.x, trunk_pos.y), "log"))
               # Add leaves
                rx = 3.25
                ry = 4.5
                top_leaf_pos = top + Vector(0, 5)
                chunk_data.append(((top_leaf_pos.x, top_leaf_pos.y), "leaf"))
                for dy in range(0, int(ry) + 1):
                    for dx in range(-int(rx), int(rx) + 1):
                        if (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry) <= 1:
                            leaf_pos = top + Vector(dx, dy)
                            chunk_data.append(((leaf_pos.x, leaf_pos.y), "leaf"))


    @staticmethod
    def ore_generation(ore_type, parameters, noise_data, ground_levels, chunk_data):
        ore_positions = set()
    
        for y_pos in range(CHUNK_SIZE):
            for x_pos in range(CHUNK_SIZE):
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
    def generate_caves(chunk_origin, cave_scale_x, cave_scale_y, cave_octaves, cave_persistence,
                    surface_threshold, mid_threshold, deep_threshold, ground_levels, noise_data, smoothstep_func):
        for y_index in range(CHUNK_SIZE):
            for x_index in range(CHUNK_SIZE):
                pos = chunk_origin + Vector(x_index, y_index)
                ground_level = ground_levels[x_index]

                # Generate base noise and detail noise
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
        chunk_data = []
        tree_positions = [] 
        chunk_origin = Vector(x, y) * CHUNK_SIZE
        tree_threshold = 0.98  #smaller = more trees, bigger = less trees
        
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
                "scale": 0.042,       # smaller scale = bigger, spread-out veins
                "threshold": 0.72,   # Lower threshold = more common
                "base": 1000,        # Unique noise pattern
                "min_depth": 8,      # Shallowest depth
            },
            "iron": {
                "scale": 0.048,       # Smaller scale = tighter veins
                "threshold": 0.76,
                "base": 2500,
                "min_depth": 40,
            },
            "gold": {
                "scale": 0.052,    
                "threshold": 0.8,    # Slightly higher threshold = slightly rarer
                "base": 4500,
                "min_depth": 70,
            }
        }
        
        # First calculate ground levels
        ground_levels = []
        for x_pos in range(CHUNK_SIZE):
            pos_x = chunk_origin.x + x_pos
            height_noise = noise.pnoise1(pos_x * terrain_scale, repeat=9999999, base=0)
            ground_levels.append(16 - math.floor(height_noise * 10))
           
        
       # Single-threaded cave generation
       # Pre-allocate noise_data as a 2D array
        noise_data = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        
        self.generate_caves(
            chunk_origin, cave_scale_x, cave_scale_y, cave_octaves, cave_persistence,
            surface_threshold, mid_threshold, deep_threshold, ground_levels, noise_data, ServerGame.smoothstep
        )

        
                        
        # Generate tunnels
        if y <= 0:
            tunnel_gen = TunnelGenerator()
            tunnel_gen.generate_tunnels(noise_data)

            # Add tunnel tiles to chunk_data
            for y_pos in range(CHUNK_SIZE):
                for x_pos in range(CHUNK_SIZE):
                    pos, is_cave, is_tunnel = noise_data[y_pos][x_pos]
                    if is_tunnel:
                        chunk_data.append([(pos.x, pos.y), None])

        # Generate ores
        for ore_type, parameters in ore_parameters.items():
            self.ore_generation(ore_type, parameters, noise_data, ground_levels, set())
           
            
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
                    self.tree_generation(chunk_origin,ground_level, pos, tree_threshold, tree_positions, chunk_data)
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

        target_chunk = f"{chunk_x};{chunk_y}"
        
        
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
        # Register all actors at once
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
            new_base_chunk = ((pos + CHUNK_SIZE/2) / CHUNK_SIZE).floored
        

        
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
            

