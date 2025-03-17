from engine.renderer import Renderer
from engine.console import Console
from engine.network import *
#?ifdef ENGINE
from engine.builder import *
#?endif

from components.actor import Actor
from components.rigidbody import Rigidbody
from components.character import Character
from components.material import Material
from components.button import Button
from components.background import Background
from components.level import Level
from components.text import Text
from components.widget import Widget
from components.datatypes import *
from components.game_math import *

#?ifdef CLIENT
from engine.gl_wrapper import *
#?endif

#?ifdef CLIENT
import pygame 
#?endif

import threading
import time
from abc import ABC



class Engine(ABC):
    def __init__(self):
        self.__running = True

        self.__world_mouse_pos = Vector()

        #?ifdef ENGINE
        self.builder = Builder("./build", "./packaged", ["./src"], ["./src", "./res"])
        #?endif


    @property
    def running(self):
        return self.__running

    
    @property
    def world_mouse_pos(self):
        return self.__world_mouse_pos


    @staticmethod
    def get_player_actor(player_id):
        return "__Player_" + str(player_id)


    def stop(self):
        self.__running = False




#?ifdef CLIENT
class InfoText(Text):
    def __init__(self, name, pos_y, pre_text, after_text = ""):
        super().__init__(name, Vector(10, pos_y * 24 + 10), Vector(215, 24), 0, "res/fonts/arial.ttf", Color(0, 0, 0, 100), text_color=Color(0, 0, 255), font_size=20, text_alignment=Alignment.LEFT)

        self.pre_text = pre_text
        self.after_text = after_text


    def set_value(self, value):
        self.text = f" {self.pre_text}{value:.1f}{self.after_text}"



class ClientEngine(Engine, Renderer):
    def __init__(self):
        Engine.__init__(self)
        Renderer.__init__(self, Vector(1600, 900), 10, "Game", False, True, Vector())

        self.fps = 120
        self.tps = 20

        self.__network = None
        self.__level = Level("Engine_Level", Character)

        self.__widgets = {}
        self.__backgrounds = {}
        self.__pressed_keys = set()
        self.__released_keys = set()
        self.__screen_mouse_pos = Vector()

        self.current_background = None

        self.__network_commands = {
            "register_actor": self.__register_actor,
            "update_actor": self.__update_actor,
            "destroy_actor": self.__destroy_actor,
            "background": self.__background,
        }

        self.__actor_templates = {
            "Actor": Actor,
            "Rigidbody": Rigidbody,
            "Character": Character,
        }

        pygame.init()

        self.__clock = pygame.time.Clock()

        self.__stats = {
            "fps":              [0] * 30,
            "events":           [0] * 30,
            "render_regs":      [0] * 30,
            "bg_render":        [0] * 30,
            "render":           [0] * 30,
            "actor_render":     [0] * 30,
            "widget_render":    [0] * 30,
            "network":          [0] * 30,
        }

        self.register_widget(InfoText("fps",            0, "fps: "))
        self.register_widget(InfoText("events",         1, "events: ",        " ms"))
        self.register_widget(InfoText("render_regs",    2, "render regs: ",   " ms"))
        self.register_widget(InfoText("bg_render",      3, "bg render: ",     " ms"))
        self.register_widget(InfoText("render",         4, "render: ",        " ms"))
        self.register_widget(InfoText("actor_render",   5, "actor render: ",  " ms"))
        self.register_widget(InfoText("widget_render",  6, "widget render: ", " ms"))
        self.register_widget(InfoText("network",        7, "network: ",       " ms"))


    @property
    def fps(self):
        return self.__fps
    

    @fps.setter
    def fps(self, value):
        if isinstance(value, int) and value > 0:
            self.__fps = value
        else:
            raise TypeError("FPS must be a positive integer:", value)
        

    @property
    def tps(self):
        return self.__tps
    

    @tps.setter
    def tps(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__tps = value
        else:
            raise TypeError("TPS must be a positive number:", value)
        

    @property
    def current_background(self):
        return self.__current_background
    

    @current_background.setter
    def current_background(self, value):
        if value in self.backgrounds or value is None:
            self.__current_background = value
        else:
            raise Exception(f"Background {value} is not registered")
        

    @property
    def widgets(self):
        return self.__widgets


    @property
    def backgrounds(self):
        return self.__backgrounds


    @property
    def network(self):
        return self.__network
    

    @property
    def level(self):
        return self.__level
         

    @property
    def pressed_keys(self):
        return self.__pressed_keys
    

    @property
    def released_keys(self):
        return self.__released_keys
            

    @property
    def screen_mouse_pos(self):
        return self.__screen_mouse_pos
    

    def show_all_stats(self):
        for name, _ in self.__stats.items():
            self.widgets[name].visible = True


    def hide_all_stats(self):
        for name, _ in self.__stats.items():
            self.widgets[name].visible = False


    def add_actor_template(self, actor):
        if not issubclass(actor, Actor):
            raise Exception(f"Actor template {actor.__name__} is already registered or wrong data type")
        self.__actor_templates[actor.__name__] = actor
    

    def register_widget(self, widget):
        if widget.name in self.__widgets or not isinstance(widget, Widget):
            raise Exception(f"Widget {widget.name} is already registered or wrong data type")
        self.__widgets[widget.name] = widget


    def register_background(self, background):
        if background.name in self.__backgrounds or not isinstance(background, Background):
            raise Exception(f"Background {background.name} is already registered or wrong data type")
        self.__backgrounds[background.name] = background
    

    def regisrer_network_command(self, cmd, func):
        if isinstance(cmd, str) and callable(func) and cmd not in self.__network_commands:
            self.__network_commands[cmd] = func
        else:
            raise TypeError("Command must be a string and function must be a function:", cmd, func)


    def destroy_actor(self, actor_name):
        if actor_name in self.actors:
            self.__actors_to_destroy.add(actor_name)
    

    def connect(self, address, port):
        self.__network = ClientNetwork(address, port)


    def join_level(self, level_name):
        self.network.send("join_level", level_name)
        self.network.send("update_distance", (self.camera_width // 16 + 1) // 2)


    def tick(self):
        delta_time = self.__clock.tick(self.fps) / 1000

        self.__stats["fps"].append(1 / delta_time / 1000)
        self.__stats["fps"].pop(0)

        self.__time_now = time.time()

        self.__handle_events()
        
        self.__time("events")

        if not self.running:
            pygame.quit()
            return delta_time

        for actor in self.__level.actors.values():
            if actor.visible and actor.material:
                self.add_actor_to_draw(actor)

        for widget in self.widgets.values():
            if widget.visible:
                self.add_widget_to_draw(widget)
                if isinstance(widget, Button):
                    widget.tick(self.pressed_keys, Keys.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)

        self.__time("render_regs")

        if self.current_background:
            self.draw_background(self.backgrounds[self.current_background])
        else:
            self.screen.fill((0, 0, 0))

        self.__time("bg_render")

        for name, stat in self.__stats.items():
            self.widgets[name].set_value(sum(stat) / len(stat) * 1000)

        render_time = self.render()

        self.__time("render")

        self.__stats["actor_render"].append(render_time[0])
        self.__stats["widget_render"].append(render_time[1])
        self.__stats["actor_render"].pop(0)
        self.__stats["widget_render"].pop(0)

        self.__handle_network()

        self.__time("network")

        return delta_time


    def __handle_network(self):
        if not self.network:
            return
        while True:
            data = self.network.get_data()
            if not data:
                break
            cmd, data = data

            if cmd in self.__network_commands:
                self.__network_commands[cmd](data)
            else:
                print(f"[Client] Unknown network request: {cmd}")
    

    def __update_mouse_pos(self, screen_pos):
        self.__screen_mouse_pos = screen_pos
        if self.network and self.network.id != -1:
            world_mouse_pos = (screen_pos - self.resolution / 2) * self.camera_width / self.resolution.x + self.camera_position
            self.network.send("world_mouse_pos", world_mouse_pos)


    def __handle_events(self):
        self.__released_keys.clear()
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.stop()
                    if self.network:
                        self.network.stop()

                case pygame.MOUSEBUTTONDOWN:
                    self.__pressed_keys.add(Keys(event.button))
                    if self.network and self.network.id != -1:
                        self.network.send("key_down", Keys(event.button))

                case pygame.MOUSEBUTTONUP:
                    self.__pressed_keys.remove(Keys(event.button))
                    self.__released_keys.add(Keys(event.button))
                    if self.network and self.network.id != -1:
                        self.network.send("key_up", Keys(event.button))

                case pygame.KEYDOWN:
                    self.__pressed_keys.add(event.key)
                    if self.network and self.network.id != -1:
                        self.network.send("key_down", event.key)

                case pygame.KEYUP:
                    self.__pressed_keys.remove(event.key)
                    self.__released_keys.add(event.key)
                    if self.network and self.network.id != -1:
                        self.network.send("key_up", event.key)

        screen_mouse_position = Vector(*pygame.mouse.get_pos())
        self.__update_mouse_pos(screen_mouse_position)


    def __time(self, stat_name):
        time_after = time.time()
        self.__stats[stat_name].append(time_after - self.__time_now)
        self.__stats[stat_name].pop(0)
        self.__time_now = time_after


    def __register_actor(self, data):
        if data["name"] in self.__level.actors:
            return
        
        if data["type"] not in self.__actor_templates:
            raise Exception(f"Actor template {data['type']} is not registered")

        self.__level.register_actor(self.__actor_templates[data["type"]](self, data["name"], data["position"])) # if it crashes in this line, it's because actor class you provided doesn't have correct attributes. It should have only engine_ref, name, position, everything else should be hardcoded


    def __update_actor(self, data):
        actor = data[0]
        if actor in self.__level.actors:
            self.__level.actors[actor].update_from_net_sync(data[1])


    def __destroy_actor(self, data):
        self.__level.destroy_actor(data)


    def __background(self, data):
        self.current_background = data

#?endif




#?ifdef SERVER
class Player:
    def __init__(self):
        self.level = None
        self.previous_chunk = None
        self.world_mouse_pos = Vector()
        self.update_distance = 0
        self.position = Vector()
        self.triggered_keys = set()
        self.pressed_keys = set()
        self.released_keys = set()



class TPS:
    def __init__(self, max_tps):
        self.max_tps = max_tps
        self.__last_time = time.time()


    def tick(self):
        delta_time = time.time() - self.__last_time
        self.__last_time = time.time()
        min_ms = 1 / self.max_tps
        if delta_time < min_ms:
            time.sleep(min_ms - delta_time)
            delta_time = min_ms
        return delta_time        



class ServerEngine(Engine):
    def __init__(self):
        self.__max_tps = 30

        self.__network = None

        self.__players = {}
        self.__levels = {}
        self.__registered_keys = {}

        self.__console = Console()
        self.__cmd_thread = threading.Thread(target=self.console.run)
        self.__cmd_thread.daemon = True
        self.__cmd_thread.start()        

        super().__init__()

        self.__stats = {
            "tps":              [0] * 30,
            "console_cmds":     [0] * 30,
            "level_updates":    [0] * 30,
            "widget_tick":      [0] * 30,
            "network":          [0] * 30,
        }

        self.__network_commands = {
            "join_level": self.__join_level,
            "world_mouse_pos": self.__world_mouse_pos,
            "update_distance": self.__update_distance,
            "key_down": self.__key_down,
            "key_up": self.__key_up,
        }

        self.__clock = TPS(self.max_tps)


    @property
    def console(self):
        return self.__console
    

    @property
    def max_tps(self):
        return self.__max_tps
    

    @max_tps.setter
    def max_tps(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__max_tps = value
            self.__clock.max_tps = value
        else:
            raise TypeError("TPS must be a positive number:", value)


    @property
    def network(self):
        return self.__network
    

    @property
    def players(self):
        return self.__players
    

    @property
    def levels(self):
        return self.__levels
        

    def register_level(self, level):
        if level.name in self.__levels or not isinstance(level, Level):
            raise Exception(f"Level {level.name} is already registered or wrong data type")
        self.__levels[level.name] = level
    

    def register_network_command(self, cmd, func):
        if isinstance(cmd, str) and callable(func):
            self.__network_commands[cmd] = func
        else:
            raise TypeError("Command must be a string and function must be a function:", cmd, func)
        

    def register_key(self, key, press_type, func):
        if key in self.__registered_keys:
            raise Exception(f"Keys {key} is already registered")
        if not key in Keys or press_type not in KeyPressType or not callable(func):
            raise TypeError("Key must be a Keys, press_type must be a KeyPressType and func must be a function:", key, press_type, func)
        self.__registered_keys[key] = (press_type, func)
        

    def start_network(self, address, port, max_connections):
        self.__network = ServerNetwork(address, port, max_connections, self.__on_player_connect)


    def get_stat(self, stat_name):
        return f"{sum(self.__stats[stat_name]) / len(self.__stats[stat_name]) * 1000:.2f}" + (" ms" if not stat_name == "tps" else "")
    

    def tick(self):
        delta_time = self.__clock.tick()

        self.__stats["tps"].append(1 / delta_time / 1000)
        self.__stats["tps"].pop(0)

        self.__time_now = time.time()

        if self.console.cmd_output:
            self.__execute_cmd(self.console.cmd_output.pop(0))

        self.__time("console_cmds")

        for level in self.levels.values():
            for player_id, player in self.__players.items():
                if player.level == level.name:
                    self.__players[player_id].position = level.actors[self.get_player_actor(player_id)].position

            destroyed_actors = level.get_destroyed()

            if destroyed_actors:
                for player_id, player in self.__players.items():
                    if player.level == level.name:
                        for actor_name in destroyed_actors:
                            self.network.send(player_id, "destroy_actor", actor_name)

            level.tick(delta_time)

            updates = level.get_updates((player for player in self.__players.values() if player.level == level.name))
            if not updates:
                continue

            for player_id, player in self.__players.items():
                if player.level != level.name:
                    continue

                p_chk = player.previous_chunk
                c_chk = get_chunk_cords(player.position)
                
                for x in range(c_chk.rounded.x - player.update_distance, c_chk.rounded.x + player.update_distance + 1):
                    if x not in level.chunks:
                        continue
                    for y in range(c_chk.rounded.y - player.update_distance, c_chk.rounded.y + player.update_distance + 1):
                        if y not in level.chunks[x]:
                            continue

                        if max(p_chk.x, c_chk.x) - player.update_distance <= x <= min(p_chk.x, c_chk.x) + player.update_distance and max(p_chk.y, c_chk.y) - player.update_distance <= y <= min(p_chk.y, c_chk.y) + player.update_distance: #TODO fix if player distance changes
                            for actor_name, update in updates.items():
                                sync_data, chunk_num = update
                                if chunk_num == Vector(x, y):
                                    self.network.send(player_id, "update_actor", (actor_name, sync_data))

                        else:
                            for actor in level.chunks[x][y]:
                                self.network.send(player_id, "register_actor", level.actors[actor].get_for_full_net_sync())

                player.previous_chunk = c_chk

        for id in self.__players:
            if not self.__players[id].level:
                continue

            for key in self.__players[id].triggered_keys:
                if key in self.__registered_keys:
                    press_type, func = self.__registered_keys[key]
                    if press_type == KeyPressType.TRIGGER:
                        func(self, self.levels[self.players[id].level], id)

            for key in self.__players[id].pressed_keys:
                if key in self.__registered_keys:
                    press_type, func = self.__registered_keys[key]
                    if press_type == KeyPressType.HOLD:
                        func(self, self.levels[self.players[id].level], id)

            for key in self.__players[id].released_keys:
                if key in self.__registered_keys:
                    press_type, func = self.__registered_keys[key]
                    if press_type == KeyPressType.TRIGGER:
                        func(self, self.levels[self.players[id].level], id)

            self.__players[id].released_keys.clear()
            self.__players[id].triggered_keys.clear()

        self.__time("level_updates")

        self.__handle_network()

        self.__time("network")

        return delta_time
    

    def __on_player_connect(self, id):
        self.__players[id] = Player()
    

    def __handle_network(self):
        if not self.network:
            print("You forgot to call start_network")
            return
        
        while True:
            data = self.network.get_data()
            if not data:
                break

            id, data = data
            cmd, data = data

            if cmd in self.__network_commands:
                self.__network_commands[cmd](id, data)
            else:
                print(f"[Server] Unknown network request: {cmd}")


    def __execute_cmd(self, cmd):
        try:
            exec(cmd)
        except Exception as e:
            print(e)


    def __time(self, stat_name):
        time_after = time.time()
        self.__stats[stat_name].append(time_after - self.__time_now)
        self.__stats[stat_name].pop(0)
        self.__time_now = time_after


    def __full_player_sync(self, id):
        player = self.__players[id]
        level = self.levels[player.level]
        player_chunk = get_chunk_cords(player.position)
        for x in range(player_chunk.rounded.x - player.update_distance, player_chunk.rounded.x + player.update_distance + 1):
            for y in range(player_chunk.rounded.y - player.update_distance, player_chunk.rounded.y + player.update_distance + 1):
                if x in level.chunks and y in level.chunks[x]:
                    for actor in level.chunks[x][y]:
                        self.network.send(id, "register_actor", level.actors[actor].get_for_full_net_sync())

        self.network.send(id, "background", level.background)


    def __join_level(self, id, data):
        level_name = data
        if level_name in self.levels:
            self.__players[id].level = level_name
            self.levels[level_name].register_actor(self.levels[level_name].default_character(self, self.get_player_actor(id), Vector())) # if it crashes in this line, it's because character class you provided doesn't have correct attributes. It should have only engine_ref, name, position, everything else should be hardcoded
            self.__players[id].previous_chunk = get_chunk_cords(self.levels[level_name].actors[self.get_player_actor(id)].position)
            self.__full_player_sync(id)
        else:
            print(f"Level {level_name} not found")


    def __world_mouse_pos(self, id, data):
        self.__players[id].world_mouse_pos = data


    def __update_distance(self, id, data):
        self.__players[id].update_distance = data
        self.__full_player_sync(id)


    def __key_down(self, id, data):
        self.__players[id].pressed_keys.add(data)
        self.__players[id].triggered_keys.add(data)


    def __key_up(self, id, data):
        self.__players[id].pressed_keys.remove(data)
        self.__players[id].released_keys.add(data)

#?endif


