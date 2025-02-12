from engine.renderer import Renderer

from engine.console import Console

from components.button import Button
from components.datatypes import *
from components.rigidbody import Rigidbody
from components.text import Text

import pygame

import threading



class Engine(Renderer):
    def __init__(self, game):
        self.fps = game.fps_cap
        self.tps = game.min_tps

        self.__actors = {}
        self.__widgets = {}

        pygame.init()
        super().__init__(game.window_width, game.window_height, game.camera_width, game.window_title, game.fullscreen, game.windowed, game.camera_position)

        self.running = True
        self.__clock = pygame.time.Clock()

        self.__pressed_keys = set()
        self.__released_keys = set()
        self.__world_mouse_pos = Vector()
        self.__screen_mouse_pos = Vector()

        self.console = Console()
        self.__cmd_thread = threading.Thread(target=self.console.run)
        self.__cmd_thread.daemon = True
        self.__cmd_thread.start()

        self.__fps_buffer = [0] * 30
        self.register_widget(Text("fps", Vector(10, 10), Vector(100, 20), 0, "res/fonts/arial.ttf", text_color=Color(0, 255, 0), font_size=20, text_alignment=Alignment.LEFT))


    @property
    def fps(self):
        return self.__fps
    

    @fps.setter
    def fps(self, value):
        if isinstance(value, int) and value > 0:
            self.__fps = value
        else:
            raise Exception("FPS must be a positive integer:", value)


    @property
    def running(self):
        return self.__running
    

    @running.setter
    def running(self, value):
        if isinstance(value, bool):
            self.__running = value
        else:
            raise Exception("Running must be a boolean:", value)
        

    @property
    def tps(self):
        return self.__tps
    

    @tps.setter
    def tps(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__tps = value
        else:
            raise Exception("TPS must be a positive number:", value)


    @property
    def actors(self):
        return self.__actors
    

    @property
    def widgets(self):
        return self.__widgets
    

    @property
    def clock(self):
        return self.__clock
    

    @property
    def pressed_keys(self):
        return self.__pressed_keys
    

    @property
    def released_keys(self):
        return self.__released_keys
    

    @property
    def world_mouse_pos(self):
        return self.__world_mouse_pos
    

    @property
    def screen_mouse_pos(self):
        return self.__screen_mouse_pos


    def register_actor(self, actor):
        if actor.name in self.actors:
            raise Exception(f"Actor {actor.name} is already registered")
        self.__actors[actor.name] = actor


    def register_widget(self, widget):
        if widget.name in self.widgets:
            raise Exception(f"Widget {widget.name} is already registered")
        self.__widgets[widget.name] = widget


    def tick(self):
        self.clear()
        delta_time = self.clock.tick(self.fps) / 1000

        self.__fps_buffer.append(1/delta_time)
        self.__fps_buffer.pop(0)
        self.widgets["fps"].text = f"{sum(self.__fps_buffer) / len(self.__fps_buffer):.1f}"

        self.__handle_events()

        if self.console.cmd_output:
            self.__execute_cmd(self.console.cmd_output.pop(0))

        if not self.running:
            pygame.quit()
            return
        
        left_delta_time = delta_time
        while left_delta_time > 0:
            self.__physics_step(min(left_delta_time, 1/self.tps))
            left_delta_time -= 1/self.tps

        for actor in self.actors.values():
            if actor.visible:
                self.add_actor_to_draw(actor)

        for widget in self.widgets.values():
            if widget.visible:
                self.add_widget_to_draw(widget)
                if issubclass(widget.__class__, Button):
                    widget.tick(self.pressed_keys, Key.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)

        self.render()

        return delta_time
    

    def __end(self):
        self.console.running = False
        self.running = False
    

    def __execute_cmd(self, cmd):
        try:
            exec(cmd)
        except Exception as e:
            print(e)


    def __update_mouse_pos(self, screen_pos):
        self.__world_mouse_pos = (screen_pos - self.resolution / 2) * self.camera_width / self.resolution.x + self.camera_position
        self.__screen_mouse_pos = screen_pos


    def __handle_events(self):
        self.__released_keys.clear()
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.__end()

                case pygame.MOUSEBUTTONDOWN:
                    self.__pressed_keys.add(Key(event.button))

                case pygame.MOUSEBUTTONUP:
                    self.__pressed_keys.remove(Key(event.button))
                    self.__released_keys.add(Key(event.button))

                case pygame.KEYDOWN:
                    self.__pressed_keys.add(event.key)

                case pygame.KEYUP:
                    self.__pressed_keys.remove(event.key)
                    self.__released_keys.add(event.key)
                        
        screen_mouse_position = Vector(*pygame.mouse.get_pos())
        self.__update_mouse_pos(screen_mouse_position)


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
                if isinstance(actor1, Rigidbody):
                    for actor2 in self.actors.values():
                        if actor2 is not actor1:
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
                            collided_actors_directions[actor1.name] = Vector(0, 0)
                        collided_actors_directions[actor1.name] += direction
                        actor1.half_size -= kinda_small_number

        for name, direction in collided_actors_directions.items():
            dn = direction.normalized
            if dn.x != 0:
                dn.x /= abs(dn.x)
            if dn.y != 0:
                dn.y /= abs(dn.y)
            self.actors[name].collided_sides = dn
