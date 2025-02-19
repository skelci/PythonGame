from engine.renderer import Renderer

from engine.console import Console

from components.button import Button
from components.datatypes import *
from components.rigidbody import Rigidbody
from components.text import Text

from components.game_math import *

import pygame

import threading



class Engine(Renderer):
    def __init__(self):
        super().__init__(1600, 900, 10, "Game", False, True, Vector())
        self.fps = 120
        self.tps = 100
        self.simulation_speed = 1

        self.__actors = {}
        self.__widgets = {}
        self.__backgrounds = {}
        self.__pressed_keys = set()
        self.__released_keys = set()
        self.__actors_to_destroy = set()
        self.__fps_buffer = [0] * 30

        self.current_background = None

        self.__clock = pygame.time.Clock()
        self.__world_mouse_pos = Vector()
        self.__screen_mouse_pos = Vector()

        self.console = Console()
        self.__cmd_thread = threading.Thread(target=self.console.run)
        self.__cmd_thread.daemon = True
        
        self.register_widget(Text("fps", Vector(10, 10), Vector(100, 20), 0, "res/fonts/arial.ttf", text_color=Color(0, 255, 0), font_size=20, text_alignment=Alignment.LEFT))
        
        self.__cmd_thread.start()
        
        pygame.init()
        self.running = True


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
    def simulation_speed(self):
        return self.__simulation_speed
    

    @simulation_speed.setter
    def simulation_speed(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__simulation_speed = value
        else:
            raise TypeError("Simulation speed must be a positive number:", value)


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
    def pressed_keys(self):
        return self.__pressed_keys
    

    @property
    def released_keys(self):
        return self.__released_keys
        

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
    def clock(self):
        return self.__clock
    

    @property
    def world_mouse_pos(self):
        return self.__world_mouse_pos
    

    @property
    def screen_mouse_pos(self):
        return self.__screen_mouse_pos


    @property
    def running(self):
        return self.__running
    

    @running.setter
    def running(self, value):
        if isinstance(value, bool):
            self.__running = value
        else:
            raise TypeError("Running must be a boolean:", value)


    def register_actor(self, actor):
        if actor.name in self.actors:
            raise Exception(f"Actor {actor.name} is already registered")
        self.__actors[actor.name] = actor


    def destroy_actor(self, actor_name):
        if actor_name in self.actors:
            self.__actors_to_destroy.add(actor_name)


    def register_widget(self, widget):
        if widget.name in self.widgets:
            raise Exception(f"Widget {widget.name} is already registered")
        self.__widgets[widget.name] = widget


    def register_background(self, background):
        if background.name in self.backgrounds:
            raise Exception(f"Background {background.name} is already registered")
        self.__backgrounds[background.name] = background


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
        
        delta_time *= self.simulation_speed

        left_delta_time = delta_time
        while left_delta_time > 0:
            self.__physics_step(min(left_delta_time, 1/self.tps))
            left_delta_time -= 1/self.tps

        for actor in self.actors.values():
            if actor.visible and actor.material:
                self.add_actor_to_draw(actor)

        for widget in self.widgets.values():
            if widget.visible:
                self.add_widget_to_draw(widget)
                if issubclass(widget.__class__, Button):
                    widget.tick(self.pressed_keys, Key.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)

        for actor_name in self.__actors_to_destroy:
            del self.actors[actor_name]
        self.__actors_to_destroy.clear()

        if self.current_background:
            self.draw_background(self.backgrounds[self.current_background])
        else:
            self.screen.fill((0, 0, 0))
        self.render()

        return delta_time
    

    def __end(self):
        self.console.running = False
        self.running = False
    

    def __execute_cmd(self, cmd):
        try:
            exec(cmd)
        except TypeError as e:
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
                        # if actor1.name == "Character":
                        #     if actor1.velocity.y == 0 and collided_actors_directions[actor1.name][3] != 1:
                        #         print("Grounded")
                        #     else:
                        #         print("air")

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
        
                        
    

