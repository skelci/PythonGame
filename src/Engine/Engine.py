from engine.renderer import Renderer

from components.rigidbody import Rigidbody
from components.datatypes import *

import pygame



class Engine(Renderer):
    def __init__(self, game):
        self.fps = game.fps_cap

        pygame.init()
        self.__actors = {}
        super().__init__(game.window_width, game.window_height, game.camera_width, game.window_title)

        self.running = True
        self.__clock = pygame.time.Clock()


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
    def actors(self):
        return self.__actors
    

    @property
    def clock(self):
        return self.__clock


    def register_actor(self, actor, b_render = True):
        if b_render:
            if actor.name in self.actors:
                raise Exception(f"Actor {actor.name} is already registered")
            self.__actors[actor.name] = actor


    def tick(self):
        self.clear()
        delta_time = self.clock.tick(self.fps) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        if not self.running:
            pygame.quit()
            return
        
        self.__physics_step(delta_time)

        for actor in self.actors.values():
            actor.tick(delta_time)
            if actor.visible:
                self.add_actor_to_draw(actor)

        self.render()

        return delta_time


    def __physics_step(self, delta_time):
        # 1. Move all rigidbodies based on velocity
        for actor in self.actors.values():
            if isinstance(actor, Rigidbody):
                actor.position += actor.velocity * delta_time

        # 2. Resolve collisions via simple iterative approach
        max_iterations = 10
        collisions_resolved = True

        while collisions_resolved and max_iterations > 0:
            collisions_resolved = False
            corrected_actors = {}

            for actor1 in self.actors.values():
                if isinstance(actor1, Rigidbody):
                    for actor2 in self.actors.values():
                        if actor2 is not actor1: # Even if second actor isn't a Rigidbody, it can still be a trigger
                            # Determine direction to push out of collision
                            direction = actor1.collision_response_direction(actor2)    
                            # Check collision
                            if not direction == Vector(0, 0):
                                collisions_resolved = True
                                corrected_actors[actor1.name] = direction

            # Apply corrections
            for name, direction in corrected_actors.items():
                self.actors[name].position += direction
            max_iterations -= 1
