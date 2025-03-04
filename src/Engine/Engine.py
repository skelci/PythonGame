from engine.renderer import Renderer
from engine.console import Console
from engine.builder import *
from engine.network import *

from components.actor import Actor
from components.button import Button
from components.background import Background
from components.level import Level
from components.text import Text
from components.widget import Widget
from components.datatypes import *
from components.game_math import *

#?ifdef CLIENT
import pygame # type: ignore
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


    def stop(self):
        self.__running = False




#?ifdef CLIENT
class InfoText(Text):
    def __init__(self, name, pos, pre_text, after_text = ""):
        super().__init__(name, pos, Vector(215, 24), 0, "res/fonts/arial.ttf", Color(0, 0, 0, 100), text_color=Color(0, 0, 255), font_size=20, text_alignment=Alignment.LEFT)

        self.pre_text = pre_text
        self.after_text = after_text


    def set_value(self, value):
        self.text = f" {self.pre_text}{value:.1f}{self.after_text}"



class ClientEngine(Engine, Renderer):
    def __init__(self):
        Engine.__init__(self)
        Renderer.__init__(self, 1600, 900, 10, "Game", False, True, Vector())

        self.fps = 120
        self.tps = 20

        self.__actors = {}
        self.__widgets = {}
        self.__backgrounds = {}

        self.current_background = None
        self.__network = None

        self.__network_commands = {}

        self.__pressed_keys = set()
        self.__released_keys = set()
        self.__screen_mouse_pos = Vector()

        self.__actors_to_destroy = set()
        
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

        self.register_widget(InfoText("fps",            Vector(10, 12 ), "fps: "))
        self.register_widget(InfoText("events",         Vector(10, 36 ), "events: ",        " ms"))
        self.register_widget(InfoText("render_regs",    Vector(10, 108), "render regs: ",   " ms"))
        self.register_widget(InfoText("bg_render",      Vector(10, 132), "bg render: ",     " ms"))
        self.register_widget(InfoText("render",         Vector(10, 156), "render: ",        " ms"))
        self.register_widget(InfoText("actor_render",   Vector(10, 180), "actor render: ",  " ms"))
        self.register_widget(InfoText("widget_render",  Vector(10, 204), "widget render: ", " ms"))
        self.register_widget(InfoText("network",        Vector(10, 228), "network: ",       " ms"))
        

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
    def actors(self):
        return self.__actors
    

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
    def pressed_keys(self):
        return self.__pressed_keys
    

    @property
    def released_keys(self):
        return self.__released_keys
            

    @property
    def screen_mouse_pos(self):
        return self.__screen_mouse_pos
    

    def regisrer_network_command(self, cmd, func):
        if isinstance(cmd, str) and callable(func):
            self.__network_commands[cmd] = func
        else:
            raise TypeError("Command must be a string and function must be a function:", cmd, func)
    

    def register_actor(self, actor):
        if actor.name in self.actors or not issubclass(actor.__class__, Actor):
            raise Exception(f"Actor {actor.name} is already registered or wrong data type")
        self.__actors[actor.name] = actor


    def register_widget(self, widget):
        if widget.name in self.widgets or not issubclass(widget.__class__, Widget):
            raise Exception(f"Widget {widget.name} is already registered or wrong data type")
        self.__widgets[widget.name] = widget


    def register_background(self, background):
        if background.name in self.backgrounds or not issubclass(background.__class__, Background):
            raise Exception(f"Background {background.name} is already registered or wrong data type")
        self.__backgrounds[background.name] = background
    

    def destroy_actor(self, actor_name):
        if actor_name in self.actors:
            self.__actors_to_destroy.add(actor_name)
    

    def connect(self, address, port):
        self.network = ClientNetwork(address, port)


    def join_level(self, level_name):
        self.network.send("join_level", level_name)
    

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
            return

        for actor in self.actors.values():
            if actor.visible and actor.material:
                self.add_actor_to_draw(actor)

        for widget in self.widgets.values():
            if widget.visible:
                self.add_widget_to_draw(widget)
                if issubclass(widget.__class__, Button):
                    widget.tick(self.pressed_keys, Key.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)         #TODO fix this

        self.__time("render_regs")

        for actor_name in self.__actors_to_destroy:
            del self.actors[actor_name]
        self.__actors_to_destroy.clear()

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
            cmd, data = self.network.get_data()
            if not data:
                break

            self.__network_commands[cmd](data)
    

    def __update_mouse_pos(self, screen_pos):
        self.__screen_mouse_pos = screen_pos
        if self.network:
            world_mouse_pos = (screen_pos - self.resolution / 2) * self.camera_width / self.resolution.x + self.camera_position
            self.network.send("world_mouse_pos", world_mouse_pos)
            self.network.send("screen_mouse_pos", screen_pos)


    def __handle_events(self):
        self.__released_keys.clear()
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.stop()
                    if self.network:
                        self.network.close()

                case pygame.MOUSEBUTTONDOWN:
                    self.__pressed_keys.add(Key(event.button))
                    if self.network:
                        self.network.send("mouse_button_down", Key(event.button))

                case pygame.MOUSEBUTTONUP:
                    self.__pressed_keys.remove(Key(event.button))
                    self.__released_keys.add(Key(event.button))
                    if self.network:
                        self.network.send("mouse_button_up", Key(event.button))

                case pygame.KEYDOWN:
                    self.__pressed_keys.add(event.key)
                    if self.network:
                        self.network.send("key_down", event.key)

                case pygame.KEYUP:
                    self.__pressed_keys.remove(event.key)
                    self.__released_keys.add(event.key)
                    if self.network:
                        self.network.send("key_up", event.key)
                        
        screen_mouse_position = Vector(*pygame.mouse.get_pos())
        self.__update_mouse_pos(screen_mouse_position)


    def __time(self, stat_name):
        time_after = time.time()
        self.__stats[stat_name].append(time_after - self.__time_now)
        self.__stats[stat_name].pop(0)
        self.__time_now = time_after

#?endif




#?ifdef SERVER
class Player:
    def __init__(self):
        self.level = None
        self.previous_chunk = None



class TPS:
    def __init__(self, max_tps):
        self.max_tps = max_tps
        self.__last_time = time.time()


    def tick(self):
        delta_time = time.time() - self.__last_time
        self.__last_time = time.time()
        if delta_time < 1 / self.max_tps:
            time.sleep(1 / self.max_tps - delta_time)
            delta_time = 1 / self.max_tps
        return delta_time        



class ServerEngine(Engine):
    def __init__(self):
        super().__init__()

        self.__max_tps = 30

        self.__network = None

        self.__levels = {}

        self.__players = {}

        self.__console = Console()
        self.__cmd_thread = threading.Thread(target=self.console.run)
        self.__cmd_thread.daemon = True
        self.__cmd_thread.start()

        self.__stats = {
            "tps":              [0] * 30,
            "console_cmds":     [0] * 30,
            "level_updates":    [0] * 30,
            "widget_tick":      [0] * 30,
            "network":          [0] * 30,
        }

        self.__network_commands = {
            "join_level": self.__join_level,
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
    def levels(self):
        return self.__levels
    

    def register_network_command(self, cmd, func):
        if isinstance(cmd, str) and callable(func):
            self.__network_commands[cmd] = func
        else:
            raise TypeError("Command must be a string and function must be a function:", cmd, func)
        

    def start_network(self, address, port, max_connections):
        self.__network = ServerNetwork(address, port, max_connections, self.__on_player_connect)
        

    def register_level(self, level):
        if level.name in self.__levels or not issubclass(level.__class__, Level):
            raise Exception(f"Level {level.name} is already registered or wrong data type")
        self.__levels[level.name] = level


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

        for level in self.__levels.values():
            level.tick(delta_time)

            updates = level.get_updates()
            if not updates:
                continue

            for player_id, player in self.__players.items():
                if player_id.level != level.name:
                    continue

                p_chk = player.previous_chunk
                c_chk = level.get_chunk_num(level.actors["__Player_" + str(player_id)].position)
                
                for x in range(c_chk.x - level.update_distance, c_chk.x + level.update_distance + 1):
                    for y in range(c_chk.y - level.update_distance, c_chk.y + level.update_distance + 1):
                        if max(p_chk.x - c_chk.x) - level.update_distance <= x <= min(p_chk.x - c_chk.x) + level.update_distance and max(p_chk.y - c_chk.y) - level.update_distance <= y <= min(p_chk.y - c_chk.y) + level.update_distance:
                            for actor_name, update in updates.items():
                                sync_data, chunk_num = update
                                if chunk_num == Vector(x, y):
                                    self.network.send(player_id, "update_actor", (actor_name, sync_data))

                        else:
                            for actor in level.chunks[x][y]:
                                self.network.send(player_id, "register_actor", actor.get_for_full_net_sync())

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
                print(f"Unknown network request: {cmd}")


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


    def __join_level(self, id, data):
        level_name = data
        if level_name in self.levels:
            self.__players[id].level = level_name
            self.levels[level_name].register_actor(self, self.levels[level_name].default_character("__Player_" + str(id)))
            self.__players[id].previous_chunk = self.levels[level_name].get_chunk_num(self.levels[level_name].actors["__Player_" + str(id)].position)
        else:
            print(f"Level {level_name} not found")

#?endif


