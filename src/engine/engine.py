
#?ifdef CLIENT
from engine.renderer import Renderer
#?endif
#?ifdef SERVER
from engine.console import Console
#?endif
#?ifdef ENGINE
from engine.builder import *
#?endif
from engine.network import *

#?ifdef CLIENT
from components.button import Button
from components.text import Text
from components.widget import Widget
#?endif
from components.actor import Actor
from components.rigidbody import Rigidbody
from components.character import Character
from components.background import Background
from components.level import Level
from components.datatypes import *
from components.game_math import *

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
class InfoText(Widget):
    def __init__(self, name, pos_y, pre_text_str):
        pre_text = Text("pre_text", Vector(), Vector(215, 20), Color(0, 255, 0), "res/fonts/arial.ttf", text=pre_text_str)
        stat_text = Text("after_text", Vector(), Vector(215, 20), Color(0, 255, 0), "res/fonts/arial.ttf")
        super().__init__(
            name,
            Vector(10, pos_y * 24 + 10),
            Vector(220, 24),
            Color(0, 0, 0, 100),
            0,
            True,
            {"pre_text": pre_text, "stat_text": stat_text},
            {"pre_text": Vector(2, 0), "stat_text": Vector(pre_text.size.x, 0)},
            {"pre_text": Alignment.CENTER_LEFT, "stat_text": Alignment.CENTER_LEFT},
        )


    def set_value(self, value):
        self.subwidgets["stat_text"].text = f"{value:.1f}"



class ClientEngine(Engine, Renderer):
    def __init__(self):
        Engine.__init__(self)
        Renderer.__init__(self, 1600, 900, 10, "Game", False, True, Vector())

        self.__update_distance = self.camera_width // (chunk_size * 2)

        self.fps = 120
        self.tps = 20

        self.__network = None
        self.__level = Level("Engine_Level", Character)
        self.__level.engine_ref = self

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

        network_thread = threading.Thread(target=self.__handle_network)
        network_thread.daemon = True
        network_thread.start()

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
        self.register_widget(InfoText("events",         1, "events: "))
        self.register_widget(InfoText("render_regs",    2, "render regs: "))
        self.register_widget(InfoText("bg_render",      3, "bg render: "))
        self.register_widget(InfoText("render",         4, "render: "))
        self.register_widget(InfoText("actor_render",   5, "actor render: "))
        self.register_widget(InfoText("widget_render",  6, "widget render: "))
        self.register_widget(InfoText("network",        7, "network: "))


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
    

    @property
    def update_distance(self):
        return self.__update_distance
    

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
    

    def connect(self, address, port):
        self.__network = ClientNetwork(address, port)


    def join_level(self, level_name):
        self.network.send("join_level", level_name)
        self.network.send("update_distance", self.__update_distance)


    def set_camera_width(self, width):
        self.camera_width = width
        self.__update_distance = self.camera_width // 16 + 1
        if self.network:
            self.network.send("update_distance", self.__update_distance)


    def tick(self):
        self.clear()

        delta_time = self.__clock.tick(self.fps) / 1000

        self.__stats["fps"].append(1 / delta_time / 1000)
        self.__stats["fps"].pop(0)

        self.__time_now = time.time()

        self.__handle_events()
        
        self.__time("events")

        if not self.running:
            pygame.quit()
            return delta_time

        for widget in self.widgets.values():
            if widget.visible:
                self.add_widget_to_draw(widget)
                if isinstance(widget, Button):
                    widget.tick(self.pressed_keys, Keys.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)

        if self.get_player_actor(self.network.id) in self.level.actors:
            player_actor = self.level.actors[self.get_player_actor(self.network.id)]
            player_chunk = get_chunk_cords(player_actor.position)
            bl_chk_pos = player_chunk - self.__update_distance - 2
            tr_chk_pos = player_chunk + self.__update_distance + 2

            for chk_x, chk_column in self.level.chunks.items():
                for chk_y, chk_actors in chk_column.items():
                    if not is_in_rect(bl_chk_pos, tr_chk_pos, Vector(chk_x, chk_y)):
                        for actor in chk_actors:
                            self.level.destroy_actor(self.level.actors[actor])

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

        self.handle_network()
        new_actors = self.level.get_new_actors()
        for actor in new_actors:
            self.add_actor_to_draw(actor)
        old_actors = self.level.get_destroyed()
        for actor in old_actors:
            self.remove_actor_from_draw(actor)

        self.__time("network")

        return delta_time


    def handle_network(self):
        if not self.network:
            return
        
        self.network.tick()


    def __handle_network(self):
        while not self.network:
            time.sleep(0.1)

        sleep_time = 1 / self.fps / 2
        while True:
            buffer = self.network.get_data(10)
            if not buffer:
                time.sleep(sleep_time)

            for cmd, data in buffer:
                if cmd in self.__network_commands:
                    self.__network_commands[cmd](data)
                else:
                    print(f"[Client] Unknown network request: {cmd}")
    

    def __update_mouse_pos(self, screen_pos):
        self.__screen_mouse_pos = screen_pos
        if self.network and self.network.id > 1:
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
                    if self.network and self.network.id > 1:
                        self.network.send("key_down", Keys(event.button))

                case pygame.MOUSEBUTTONUP:
                    self.__pressed_keys.remove(Keys(event.button))
                    self.__released_keys.add(Keys(event.button))
                    if self.network and self.network.id > 1:
                        self.network.send("key_up", Keys(event.button))

                case pygame.KEYDOWN:
                    self.__pressed_keys.add(event.key)
                    if self.network and self.network.id > 1:
                        self.network.send("key_down", event.key)

                case pygame.KEYUP:
                    self.__pressed_keys.remove(event.key)
                    self.__released_keys.add(event.key)
                    if self.network and self.network.id > 1:
                        self.network.send("key_up", event.key)

        screen_mouse_position = Vector(*pygame.mouse.get_pos())
        self.__update_mouse_pos(screen_mouse_position)


    def __time(self, stat_name):
        time_after = time.time()
        self.__stats[stat_name].append(time_after - self.__time_now)
        self.__stats[stat_name].pop(0)
        self.__time_now = time_after


    def __register_actor(self, data):
        if data[1] in self.__level.actors:
            return
        
        if data[0] not in self.__actor_templates:
            raise Exception(f"Actor template {data[0]} is not registered")

        self.__level.register_actor(self.__actor_templates[data[0]](data[1], data[2])) # if it crashes in this line, it's because actor class you provided doesn't have correct attributes. It should have only name, position, everything else should be hardcoded


    def __update_actor(self, data):
        actor_name = data[0]
        if actor_name in self.__level.actors:
            self.__level.actors[actor_name].update_from_net_sync(data[1])

            if "position" not in data[1]:
                return

            actor = self.__level.actors[actor_name]
            chk_x, chk_y = get_chunk_cords(actor.position)
            a_chk_x, a_chk_y = actor.chunk
            if a_chk_x != chk_x or a_chk_y != chk_y:
                self.level.chunks[a_chk_x][a_chk_y].remove(actor.name)
                self.level.add_actor_to_chunk(actor)


    def __destroy_actor(self, data):
        self.__level.destroy_actor(data)


    def __background(self, data):
        self.current_background = data

#?endif




#?ifdef SERVER
class Player:
    def __init__(self):
        self.level = ""
        self.previous_chunk = Vector()
        self.previous_different_chunk = Vector()
        self.synced_chuks = set()
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
        super().__init__()

        self.__max_tps = 30

        self.__network = None

        self.__players = {}
        self.__levels = {}
        self.__registered_keys = {}

        self.__console = Console()
        self.__cmd_thread = threading.Thread(target=self.console.run)
        self.__cmd_thread.daemon = True
        self.__cmd_thread.start()

        self.__stats = {
            "tps":              [0] * 30,
            "console_cmds":     [0] * 30,
            "level_updates":    [0] * 30,
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
        level.engine_ref = self
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
    
    
    @staticmethod
    def package_as_chunks(actors):
        chunks = {}
        for actor in actors:
            chunk = get_chunk_cords(actor.position)
            if chunk.x not in chunks:
                chunks[chunk.x] = {}
            if chunk.y not in chunks[chunk.x]:
                chunks[chunk.x][chunk.y] = []
            chunks[chunk.x][chunk.y].append(actor)
        return chunks
    

    @staticmethod
    def get_actors_from_chk_pkg(chk_pkd, bottom_left, top_right, add_method=lambda a, el: a.extend(el)):
        actors = []
        for x in range(bottom_left.x, top_right.x + 1):
            if x not in chk_pkd:
                continue
            for y in range(bottom_left.y, top_right.y + 1):
                if y not in chk_pkd[x]:
                    continue
                add_method(actors, chk_pkd[x][y])

        return actors


    def tick(self):
        delta_time = self.__clock.tick()

        self.__stats["tps"].append(1 / delta_time / 1000)
        self.__stats["tps"].pop(0)

        if delta_time > 1 / 20:
            delta_time = 1 / 20

        self.__time_now = time.time()

        if self.console.cmd_output:
            self.__execute_cmd(self.console.cmd_output.pop(0))

        self.__time("console_cmds")

        for level in self.levels.values():
            new_actors = level.get_new_actors()
            destroyed_actors = level.get_destroyed()
            updates_pkg = level.get_updates((player for player in self.__players.values() if player.level == level.name))

            new_actors_pkg = self.package_as_chunks(new_actors)
            destroyed_actors_pkg = self.package_as_chunks(destroyed_actors)

            level.tick(delta_time)

            for player_id, player in self.__players.items():
                if player.level != level.name:
                    continue

                player.position = level.actors[self.get_player_actor(player_id)].position
                c_chk = get_chunk_cords(player.position)
                p_chk = player.previous_chunk.copy
                pd_chk = player.previous_different_chunk.copy
                if p_chk != c_chk:
                    player.previously_loaded_chunk = p_chk
                player.previous_chunk = c_chk
                
                bl_chk_pos = Vector(
                    min((get_chunk_cords(player.position).x - player.update_distance), pd_chk.x - player.update_distance),
                    min((get_chunk_cords(player.position).y - player.update_distance), pd_chk.y - player.update_distance)
                ).rounded - 1
                tr_chk_pos = Vector(
                    max((get_chunk_cords(player.position).x + player.update_distance), pd_chk.x + player.update_distance),
                    max((get_chunk_cords(player.position).y + player.update_distance), pd_chk.y + player.update_distance)
                ).rounded

                for actor in self.get_actors_from_chk_pkg(new_actors_pkg, bl_chk_pos, tr_chk_pos):
                    self.network.send(player_id, "register_actor", actor.get_for_full_net_sync())

                for actor in self.get_actors_from_chk_pkg(destroyed_actors_pkg, bl_chk_pos, tr_chk_pos):
                    self.network.send(player_id, "destroy_actor", actor.name)

                for actor_dict in self.get_actors_from_chk_pkg(updates_pkg, bl_chk_pos, tr_chk_pos, lambda a, el: a.append(el)):
                    for actor_name, sync_data in actor_dict.items():
                        if "visible" in sync_data:
                            visible = sync_data["visible"]
                            if not visible:
                                self.network.send(player_id, "destroy_actor", actor_name)
                            else:
                                self.network.send(player_id, "register_actor", level.actors[actor_name].get_for_full_net_sync())
                            continue
                            
                        self.network.send(player_id, "update_actor", (actor_name, sync_data), True)

                prev_synced_chunks = player.synced_chuks.copy()
                player.synced_chuks.clear()
                for x in range(c_chk.rounded.x - player.update_distance, c_chk.rounded.x + player.update_distance + 1):
                    for y in range(c_chk.rounded.y - player.update_distance, c_chk.rounded.y + player.update_distance + 1):
                        player.synced_chuks.add(Vector(x, y))

                        if x not in level.chunks:
                            continue
                        if y not in level.chunks[x]:
                            continue

                        if Vector(x, y) in prev_synced_chunks:
                            continue
                        for actor in level.chunks[x][y]:
                            self.network.send(player_id, "register_actor", level.actors[actor].get_for_full_net_sync())

        self.__time("level_updates")

        self.__handle_network()

        self.__time("network")

        return delta_time
    

    def __on_player_connect(self, id):
        self.__players[id] = Player()
    

    def __handle_network(self):
        self.network.tick()

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

        if not self.network:
            print("You forgot to call start_network")
            return

        data_buffer = self.network.get_data(100)
        for id, packed_data in data_buffer:
            cmd, data = packed_data

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


    def on_connect(self, id):
        level = self.levels[self.players[id].level]
        self.network.send(id, "background", level.background)


    def __join_level(self, id, data):
        level_name = data
        if level_name in self.levels:
            self.__players[id].level = level_name
            player_actor = self.levels[level_name].default_character(self.get_player_actor(id), Vector()) # if it crashes in this line, it's because character class you provided doesn't have correct attributes. It should have only name, position, everything else should be hardcoded
            self.levels[level_name].register_actor(player_actor)
            self.__players[id].previous_chunk = get_chunk_cords(player_actor.position)
            self.__players[id].previous_different_chunk = self.__players[id].previous_chunk
            self.on_connect(id)
        else:
            print(f"Level {level_name} not found")


    def __world_mouse_pos(self, id, data):
        self.__players[id].world_mouse_pos = data


    def __update_distance(self, id, data):
        self.__players[id].update_distance = data


    def __key_down(self, id, data):
        self.__players[id].pressed_keys.add(data)
        self.__players[id].triggered_keys.add(data)


    def __key_up(self, id, data):
        if data in self.__players[id].pressed_keys:
            self.__players[id].pressed_keys.remove(data)
        self.__players[id].released_keys.add(data)

#?endif


