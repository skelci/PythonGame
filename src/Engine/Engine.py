from engine.renderer import Renderer

from engine.console import Console
from engine.builder import *
from engine.network import *

from components.button import Button
from components.actor import Actor
from components.widget import Widget
from components.background import Background
from components.datatypes import *
from components.game_math import *
from components.rigidbody import Rigidbody
from components.text import Text

#?ifdef CLIENT
import pygame # type: ignore
#?endif

import threading
import time
from abc import ABC, abstractmethod



#?ifdef CLIENT
class InfoText(Text):
    def __init__(self, name, pos, pre_text, after_text = ""):
        super().__init__(name, pos, Vector(215, 24), 0, "res/fonts/arial.ttf", Color(0, 0, 0, 100), text_color=Color(0, 0, 255), font_size=20, text_alignment=Alignment.LEFT)

        self.pre_text = pre_text
        self.after_text = after_text


    def set_value(self, value):
        self.text = f" {self.pre_text}{value:.1f}{self.after_text}"

#?endif



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
        }

        self.register_widget(InfoText("fps",            Vector(10, 12 ), "fps: "))
        self.register_widget(InfoText("events",         Vector(10, 36 ), "events: ",        " ms"))
        self.register_widget(InfoText("render_regs",    Vector(10, 108), "render regs: ",   " ms"))
        self.register_widget(InfoText("bg_render",      Vector(10, 132), "bg render: ",     " ms"))
        self.register_widget(InfoText("render",         Vector(10, 156), "render: ",        " ms"))
        self.register_widget(InfoText("actor_render",   Vector(10, 180), "actor render: ",  " ms"))
        self.register_widget(InfoText("widget_render",  Vector(10, 204), "widget render: ", " ms"))
        

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

        return delta_time
    

    def __update_mouse_pos(self, screen_pos):
        if self.network:
            world_mouse_pos = (screen_pos - self.resolution / 2) * self.camera_width / self.resolution.x + self.camera_position
            self.network.send("world_mouse_pos", world_mouse_pos)
        self.__screen_mouse_pos = screen_pos


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

        self.simulation_speed = 1
        self.__max_tps = 30

        self.__actors = {}
        self.__widgets = {}
        self.__backgrounds = {}

        self.__actors_to_destroy = set()

        self.__console = Console()
        self.__cmd_thread = threading.Thread(target=self.console.run)
        self.__cmd_thread.daemon = True
        self.__cmd_thread.start()

        self.__stats = {
            "tps":              [0] * 30,
            "console_cmds":     [0] * 30,
            "physics":          [0] * 30,
            "widget_tick":      [0] * 30,
        }

        self.__clock = TPS(self.max_tps)


    @property
    def console(self):
        return self.__console
        

    @property
    def simulation_speed(self):
        return self.__simulation_speed
    

    @property
    def max_tps(self):
        return self.__max_tps
    

    @property
    def actors(self):
        return self.__actors
    

    @property
    def widgets(self):
        return self.__widgets
    
    @property
    def backgrounds(self):
        return self.__backgrounds
    

    @max_tps.setter
    def max_tps(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__max_tps = value
            self.__clock.max_tps = value
        else:
            raise TypeError("TPS must be a positive number:", value)
    

    @simulation_speed.setter
    def simulation_speed(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__simulation_speed = value
        else:
            raise TypeError("Simulation speed must be a positive number:", value)
        

    def destroy_actor(self, actor_name):
        if actor_name in self.actors:
            self.__actors_to_destroy.add(actor_name)


    def get_stat(self, stat_name):
        return f"{stat_name}: {sum(self.__stats[stat_name]) / len(self.__stats[stat_name]) * 1000:.2f}" + (" ms" if not stat_name == "tps" else "")
    

    def tick(self):
        delta_time = self.__clock.tick()

        self.__stats["tps"].append(1 / delta_time / 1000)
        self.__stats["tps"].pop(0)

        self.__time_now = time.time()

        if self.console.cmd_output:
            self.__execute_cmd(self.console.cmd_output.pop(0))

        self.__time("console_cmds")
        
        delta_time *= self.simulation_speed

        self.__physics_step(delta_time)

        self.__time("physics")

        for widget in self.widgets.values():
            if widget.visible and issubclass(widget.__class__, Button):
                widget.tick(self.pressed_keys, Key.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)         #TODO fix this

        self.__time("widget_tick")

        for actor_name in self.__actors_to_destroy:
            del self.actors[actor_name]
        self.__actors_to_destroy.clear()

        return delta_time


    def __execute_cmd(self, cmd):
        # try:
            exec(cmd)
        # except Exception as e:
        #     print(e)

        
    def __time(self, stat_name):
        time_after = time.time()
        self.__stats[stat_name].append(time_after - self.__time_now)
        self.__stats[stat_name].pop(0)
        self.__time_now = time_after


    def __physics_step(self, delta_time):
        for actor in self.actors.values():
            actor.tick(delta_time)

        for actor in self.actors.values():
            if isinstance(actor, Rigidbody):
                actor.position += actor.velocity * delta_time

        max_iterations = 8
        collisions_not_resolved = True
        collided_actors = {}

        while collisions_not_resolved and max_iterations > 0:
            collisions_not_resolved = False
            corrected_actors = {}

            for actor1 in self.actors.values():
                if isinstance(actor1, Rigidbody) and actor1.simulate_physics:
                    for actor2 in self.actors.values():
                        if actor2 is not actor1 and actor2.collidable:
                            direction = actor1.collision_response_direction(actor2)
                            if not direction == Vector(0, 0):
                                collisions_not_resolved = True

                                if actor1.name not in corrected_actors:
                                    corrected_actors[actor1.name] = Vector(0, 0)
                                corrected_actors[actor1.name] += direction

                                if actor1.name not in collided_actors:
                                    collided_actors[actor1.name] = [None, Vector(0, 0)]
                                collided_actors[actor1.name][0] = CollisionData( direction.normalized, actor2.velocity if hasattr(actor2, "velocity") else Vector(0, 0), actor2.restitution, actor2.mass if hasattr(actor2, "mass") else float("inf"), actor2)
                                if actor2.name not in collided_actors:
                                    collided_actors[actor2.name] = [None, Vector(0, 0)]
                                collided_actors[actor2.name][0] = CollisionData(-direction.normalized, actor1.velocity, actor1.restitution, actor1.mass, actor1)

                                collided_actors[actor1.name][1] += direction

            for name, direction in corrected_actors.items():
                self.actors[name].position += direction

            max_iterations -= 1

        for name in collided_actors:
            collided_actors[name][0].normal = collided_actors[name][1].normalized
            self.actors[name].on_collision(collided_actors[name][0])

        collided_actors_directions = {}
        for actor1 in self.actors.values():
            if isinstance(actor1, Rigidbody):
                for actor2 in self.actors.values():
                    if actor2 is not actor1:
                        actor1.half_size += kinda_small_number
                        direction = actor1.collision_response_direction(actor2)
                        if actor1.name not in collided_actors_directions:
                            collided_actors_directions[actor1.name] = [0, 0, 0, 0]
                        # right, left, top, bottom
                        if direction.x < 0:
                            collided_actors_directions[actor1.name][0] = 1
                        if direction.x > 0:
                            collided_actors_directions[actor1.name][1] = 1
                        if direction.y < 0:
                            collided_actors_directions[actor1.name][2] = 1
                        if direction.y > 0:
                            collided_actors_directions[actor1.name][3] = 1
                        actor1.half_size -= kinda_small_number

        for name, direction in collided_actors_directions.items():
            self.actors[name].collided_sides = direction

        overlaped_actors = {}
        for actor1 in self.actors.values():
            if actor1.generate_overlap_events:
                actor1.half_size += kinda_small_number
                for actor2 in self.actors.values():
                    if actor1 is not actor2:
                        if is_overlapping_rect(actor1, actor2):
                            if actor2.name not in overlaped_actors:
                                overlaped_actors[actor2.name] = set()
                            overlaped_actors[actor2.name].add(actor1)
                actor1.half_size -= kinda_small_number

        for actor_name, overlaped_set in overlaped_actors.items():
            for actor in overlaped_set - self.actors[actor_name].previously_collided:
                self.actors[actor_name].on_overlap_begin(actor)
            for actor in self.actors[actor_name].previously_collided - overlaped_set:
                self.actors[actor_name].on_overlap_end(actor)

        for actor_name, overlaped_set in overlaped_actors.items():
            self.actors[actor_name].previously_collided = overlaped_set

#?endif
