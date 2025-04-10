"""
Engine core class. It is used to run the game on the client and server side.
It handles all the game logic and physics.
"""

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
from components.input_box import InputBox
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
from typing import Any, Callable



class Engine(ABC):
    """
    Common things in server and client engine.
    """


    def __init__(self):
        self.__running = True

        #?ifdef ENGINE
        self.builder = Builder("./build", "./packaged", ["./src"], ["./src", "./res"])
        #?endif


    @property
    def running(self):
        """
        bool - If True, engine is running, if False, engine is stopped.
        """
        return self.__running


    @staticmethod
    def get_player_actor(player_id: int):
        """
        Args:
            player_id: Player id. You can get it from network class on client or from players dict on server.
        Returns:
            str - player actor name. You can use it to get player actor from level.actors dict.
        """
        return "__Player_" + str(player_id)


    def stop(self):
        """
        Stop the engine. It will stop the main loop and end all threads.
        """
        self.__running = False




#?ifdef CLIENT
class InfoText(Widget):
    """
    Widget that is used to display stats in the top left corner of the screen.
    """


    def __init__(self, name: str, pos_y: int, pre_text_str: str):
        """
        Args:
            name: Widget name.
            pos_y: Number of the row in the stats table.
            pre_text_str: Text that will be displayed before the value.
        """
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


    def set_value(self, value: float):
        """
        Set the value of the displayed stat.
        Args:
            value: Value to be displayed.
        """
        self.subwidgets["stat_text"].text = f"{value:.1f}"



class ClientEngine(Engine, Renderer):
    """
    Client engine class. It is used to run the game on the client side.
    """


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
        self.__triggered_keys = set()
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
        self.__world_mouse_pos = Vector()

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
        """
        float - Maximum frames per second. Default is 120.
        """
        return self.__fps
    

    @fps.setter
    def fps(self, value):
        if isinstance(value, int) and value > 0:
            self.__fps = value
        else:
            raise TypeError("FPS must be a positive integer:", value)
        

    @property
    def current_background(self):
        """
        str - Current background name. If None, background with Color(0, 0, 0) is drawn.
        """
        return self.__current_background
    

    @current_background.setter
    def current_background(self, value):
        if value in self.backgrounds or value is None:
            self.__current_background = value
        else:
            raise Exception(f"Background {value} is not registered")
        

    @property
    def widgets(self):
        """
        dict[str, Widget] - Dictionary of all registered widgets. Key is widget name, value is widget object.
        """
        return self.__widgets


    @property
    def backgrounds(self):
        """
        dict[str, Background] - Dictionary of all registered backgrounds. Key is background name, value is background object.
        """
        return self.__backgrounds


    @property
    def network(self):
        """
        ClientNetwork - used to handle connection and authentication with server.
        """
        return self.__network
    

    @property
    def level(self):
        """
        Level - Client level object. It is used to handle all actors (including physics).
        """
        return self.__level
    

    @property
    def triggered_keys(self):
        """
        set[Keys] - Set of all keys that were pressed in the last frame.
        """
        return self.__triggered_keys
         

    @property
    def pressed_keys(self):
        """
        set[Keys] - Set of all keys that are currently pressed.
        """
        return self.__pressed_keys
    

    @property
    def released_keys(self):
        """
        set[Keys] - Set of all keys that were released in the last frame.
        """
        return self.__released_keys
            

    @property
    def screen_mouse_pos(self):
        """
        Vector - Mouse position in screen coordinates.
        """
        return self.__screen_mouse_pos
    

    @property
    def world_mouse_pos(self):
        """
        Vector - Mouse position in world coordinates. It is calculated from screen_mouse_pos, camera_width and camera_position.
        """
        return self.__world_mouse_pos
    

    @property
    def update_distance(self):
        """
        int - Distance in chunks from player to load actors. It is calculated from camera_width.
        """
        return self.__update_distance
    

    def show_all_stats(self):
        """
        Show all stats of the engine in the top left corner of the screen. It sets all stat widgets to visible.
        """
        for name, _ in self.__stats.items():
            self.widgets[name].visible = True


    def hide_all_stats(self):
        """
        Hide all stats of the engine. It sets all stat widgets to invisible.
        """
        for name, _ in self.__stats.items():
            self.widgets[name].visible = False


    def check_network(self):
        """
        Check if network is connected and if player id is valid.
        Returns:
            bool - True if network is connected and player id is valid, False otherwise.
        """
        if not self.network or self.network.id <= 0:
            return False
        return True


    def add_actor_template(self, actor: Actor):
        """
        Adds actor template to the engine. It is used to create new actors in the level when server sends them.
        Args:
            actor: Actor class. It must be subclass of Actor. It should have next parameters in __init__; name: str, pos: Vector.
        Raises:
            Exception: If actor class is already registered or if it is not subclass of Actor.
        """
        if not issubclass(actor, Actor) or actor.__name__ in self.__actor_templates:
            raise Exception(f"Actor template {actor.__name__} is already registered or wrong data type")
        self.__actor_templates[actor.__name__] = actor
    

    def register_widget(self, widget: Widget):
        """
        Registers widget in the engine. You can later access it by its name by widgets property.
        Args:
            widget: Widget object. It must be subclass of Widget.
        Raises:
            Exception: If widget is already registered or if it is not subclass of Widget.
        """
        if widget.name in self.__widgets or not isinstance(widget, Widget):
            raise Exception(f"Widget {widget.name} is already registered or wrong data type")
        self.__widgets[widget.name] = widget


    def register_background(self, background: Background):
        """
        Registers background in the engine.
        Args:
            background: Background object. It must be subclass of Background.
        Raises:
            Exception: If background is already registered or if it is not subclass of Background.
        """
        if background.name in self.__backgrounds or not isinstance(background, Background):
            raise Exception(f"Background {background.name} is already registered or wrong data type")
        self.__backgrounds[background.name] = background
    

    def regisrer_network_command(self, cmd: str, func: Callable[[Any], None]):
        """
        Registers network command in the engine. It will be called when server sends it to the client.
        Args:
            cmd: Command name. It must be unique.
            func: Function that will be called when server sends the command. It must take one argument - data.
        Raises:
            TypeError: If cmd is not string or func is not callable or cmd is already registred.
        """
        if isinstance(cmd, str) and callable(func) and cmd not in self.__network_commands:
            self.__network_commands[cmd] = func
        else:
            raise TypeError("Command must be a string and function must be a function:", cmd, func)
    

    def connect(self, address: str, port: int):
        """
        Tries to connect to the server.
        Args:
            address: Server address. It must be a string.
            port: Server port. It must be an integer.
        """
        self.__network = ClientNetwork(address, port)


    def join_level(self, level_name: str):
        """
        Join the level on the server.
        Args:
            level_name: Level name. It must be a string.
        """
        self.network.send("join_level", level_name)
        self.network.send("update_distance", self.__update_distance)


    def set_camera_width(self, width: float):
        """
        Sets the camera width.
        Args:
            width: Camera width in world units. It must be a positive number.
        """
        self.camera_width = width
        self.__update_distance = self.camera_width // 16 + 1
        if self.network:
            self.network.send("update_distance", self.__update_distance)


    def __tick_widget(self, delta_time, widget):
        if widget.visible:
            if isinstance(widget, Button):
                widget.tick(self.pressed_keys, Keys.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)
            elif isinstance(widget, InputBox):
                widget.tick(delta_time, self.triggered_keys, self.pressed_keys, self.screen_mouse_pos)
            
            if hasattr(widget, "subwidgets"):
                for subwidget in widget.subwidgets.values():
                    self.__tick_widget(delta_time, subwidget)

    def tick(self):
        """
        Ticks the engine. It handles events, updates actors, renders the screen and handles network.
        Returns:
            float - delta_time. The time elapsed since the last tick.
        """
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
        
        if self.network:
            self.network.tick()
        new_actors = self.level.get_new_actors()
        for actor in new_actors:
            self.add_actor_to_draw(actor)
        old_actors = self.level.get_destroyed()
        for actor in old_actors:
            self.remove_actor_from_draw(actor)

        self.__time("network")

        for widget in self.widgets.values():
            if widget.visible:
                self.add_widget_to_draw(widget)
                self.__tick_widget(delta_time, widget)

        if self.check_network() and self.get_player_actor(self.network.id) in self.level.actors:
            player_actor = self.level.actors[self.get_player_actor(self.network.id)]
            player_chunk = get_chunk_cords(player_actor.position)
            bl_chk_pos = player_chunk - self.__update_distance - 2
            tr_chk_pos = player_chunk + self.__update_distance + 2

            for chk_x, chk_column in self.level.chunks.items():
                for chk_y, chk_actors in chk_column.items():
                    if is_in_rect(bl_chk_pos, tr_chk_pos, Vector(chk_x, chk_y)):
                        continue

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

        return delta_time


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
        self.__triggered_keys.clear()
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.stop()
                    if self.network:
                        self.network.stop()

                case pygame.MOUSEBUTTONDOWN:
                    self.__pressed_keys.add(Keys(event.button))
                    self.__triggered_keys.add(Keys(event.button))
                    if self.check_network():
                        self.network.send("key_down", Keys(event.button))

                case pygame.MOUSEBUTTONUP:
                    self.__pressed_keys.remove(Keys(event.button))
                    self.__released_keys.add(Keys(event.button))
                    if self.check_network():
                        self.network.send("key_up", Keys(event.button))

                case pygame.KEYDOWN:
                    self.__pressed_keys.add(event.key)
                    self.__triggered_keys.add(event.key)
                    if self.check_network():
                        self.network.send("key_down", event.key)

                case pygame.KEYUP:
                    self.__pressed_keys.remove(event.key)
                    self.__released_keys.add(event.key)
                    if self.check_network():
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
        self.level.destroy_actor(self.level.actors[data])


    def __background(self, data):
        self.current_background = data

#?endif




#?ifdef SERVER
class Player:
    """
    Player class used to store some data for each connected client. It should be updated only by the engine.
    """


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
    """
    Used to limit the ticks per second of the server.
    """


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
    """
    Server engine class. It is used to run the game on the server side.
    It handles all the game logic and physics.
    """


    def __init__(self):
        super().__init__()

        self.__max_tps = 120

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
        """
        Console - Console object. It is used to handle commands from the console.
        """
        return self.__console
    

    @property
    def max_tps(self):
        """
        float - Maximum ticks per second. Default is 120.
        """
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
        """
        ServerNetwork - used to handle connection and authentication with clients.
        """
        return self.__network
    

    @property
    def players(self):
        """
        dict[int, Player] - Dictionary of all connected players. Key is player id, value is player object.
        """
        return self.__players
    

    @property
    def levels(self):
        """
        dict[str, Level] - Dictionary of all registered levels. Key is level name, value is level object.
        """
        return self.__levels
        

    def register_level(self, level: Level):
        """
        Registers level in the engine. You can later access it by its name by levels property.
        Args:
            level: Level object. It must be subclass of Level.
        Raises:
            Exception: If level is already registered or if it is not subclass of Level.
        """
        if level.name in self.__levels or not isinstance(level, Level):
            raise Exception(f"Level {level.name} is already registered or wrong data type")
        level.engine_ref = self
        self.__levels[level.name] = level
    

    def register_network_command(self, cmd: str, func: Callable[[int, Any], None]):
        """
        Registers network command in the engine. It will be called when client sends it to the server.
        Args:
            cmd: Command name. It must be unique.
            func: Function that will be called when client sends the command. It must take two arguments - id and data.
        """
        if isinstance(cmd, str) and callable(func):
            self.__network_commands[cmd] = func
        else:
            raise TypeError("Command must be a string and function must be a function:", cmd, func)
        

    def register_key(self, key: Keys, press_type: KeyPressType, func: Callable[['ServerEngine', Level, int], None]):
        """
        Registers key in the engine. It will be called based on the press type.
        Args:
            key: Key to be registered. It must be subclass of Keys.
            press_type: Press type. It must be subclass of KeyPressType.
            func: Function that will be called based on the press type. It must take three arguments - engine_ref, level_ref and player_id.
        Raises:
            TypeError: If key is not subclass of Keys or press_type is not subclass of KeyPressType or func is not callable.
            ValueError: If key is already registered.
        """
        if key in self.__registered_keys:
            raise ValueError(f"Keys {key} is already registered")
        if not key in Keys or press_type not in KeyPressType or not callable(func):
            raise TypeError("Key must be a Keys, press_type must be a KeyPressType and func must be a function:", key, press_type, func)
        self.__registered_keys[key] = (press_type, func)
        

    def start_network(self, address: str, port: int, max_connections: int):
        """
        Starts the server network.
        Args:
            address: Server address. It must be a string.
            port: Server port. It must be a positive integer.
            max_connections: Maximum number of connections. It must be a positive integer.
        """
        self.__network = ServerNetwork(address, port, max_connections, self.__on_player_connect)


    def get_stat(self, stat_name: str):
        """
        Get the value of the stat.
        Args:
            stat_name: Stat name. It must be one of the registered stats.
        Returns:
            str - Stat value in ms. If stat name is tps, it will be returned as is.
        """
        if stat_name not in self.__stats:
            raise ValueError(f"Stat {stat_name} is not registered")
        return f"{sum(self.__stats[stat_name]) / len(self.__stats[stat_name]) * 1000:.2f}" + (" ms" if not stat_name == "tps" else "")
    
    
    @staticmethod
    def package_as_chunks(actors: list[Actor]):
        """
        Packages actors in dictionary by their chunk coordinates.
        Args:
            actors: List of actors to be packaged.
        Returns:
            dict[int, dict[int, list[Actor]]] - Dictionary of actors by their chunk coordinates. Key is chunk x coordinate, value is dictionary of chunk y coordinates and list of actors in that chunk.
        """
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
    def get_actors_from_chk_pkg(chk_pkd: dict[int, dict[int, Actor]], bottom_left: Vector, top_right: Vector, add_method: Callable[[list, Actor], None] = lambda a, el: a.extend(el)):
        """
        Retrieves actors from the chunk package based on the given coordinates.
        Args:
            chk_pkd: Dictionary of actors by their chunk coordinates.
            bottom_left: Bottom left corner of the rectangle.
            top_right: Top right corner of the rectangle.
            add_method: Method to add actors to the list. Default is to extend the list with the actors.
        Returns:
            list[Actor] - List of actors in the given rectangle.
        """
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
        """
        Ticks the engine. It handles events, updates actors and handles network.
        """
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


    def on_connect(self, id: int):
        """
        Called when player connects to the server.
        Args:
            id: Player id.
        """
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


