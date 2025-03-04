from components.datatypes import *
from components.widget import Widget
from components.button import Button
from components.actor import Actor
from components.background import Background
from components.rigidbody import Rigidbody
from components.character import Character
from components.game_math import *



class Level:
    def __init__(self, name, default_character, actors = [], widgets = [], backgrounds = [], simulation_speed = 1, gravity = 1, update_distance = 2):
        self.name = name
        self.defoult_character = default_character
        self.actors = {}
        self.widgets = {}
        self.backgrounds = {}
        self.simulation_speed = simulation_speed
        self.gravity = gravity
        self.update_distance = update_distance

        self.__actors_to_destroy = set()

        for actor in actors:
            self.register_actor(actor)
        for widget in widgets:
            self.register_widget(widget)
        for background in backgrounds:
            self.register_background(background)

        self.__chunk_map = {}



    @property
    def name(self):
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string:", value)
        

    @property
    def default_character(self):
        return self.__default_character
    

    @default_character.setter
    def default_character(self, value):
        if issubclass(value.__class__, Character):
            self.__default_character = value
        else:
            raise TypeError("Default character must be a subclass of Character:", value)
        

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
    def simulation_speed(self):
        return self.__simulation_speed
    

    @simulation_speed.setter
    def simulation_speed(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__simulation_speed = value
        else:
            raise TypeError("Simulation speed must be a positive number:", value)
        

    @property
    def gravity(self):
        return self.__gravity
    

    @gravity.setter
    def gravity(self, value):
        if isinstance(value, (int, float)):
            self.__gravity = value
        else:
            raise TypeError("Gravity must be a float:", value)
        

    @property
    def update_distance(self):
        return self.__update_distance
    

    @update_distance.setter
    def update_distance(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__update_distance = value
        else:
            raise TypeError("Update distance must be a positive number:", value)
        

    @property
    def chunk_map(self):
        return self.__chunk_map
        

    def register_actor(self, actor):
        if issubclass(actor.__class__, Actor):
            self.actors[actor.name] = actor
            self.__add_actor_to_chunk(actor)
        else:
            raise TypeError("Actor must be a subclass of Actor:", actor)
        

    def destroy_actor(self, actor):
        if actor in self.actors:
            self.__actors_to_destroy.add(actor)
        else:
            raise ValueError("Actor not found in level:", actor)
        

    def register_widget(self, widget):
        if issubclass(widget.__class__, Widget):
            self.widgets[widget.name] = widget
        else:
            raise TypeError("Widget must be a subclass of Widget:", widget)
        

    def register_background(self, background):
        if issubclass(background.__class__, Background):
            self.backgrounds[background.name] = background
        else:
            raise TypeError("Background must be a subclass of Background:", background)
    

    def get_chunk_num(self, pos):
        return pos // 16
        

    #?ifdef SERVER
    def get_updates(self, positions: list):
        actor_updates = {}
        positions = set(positions)
        pos_copy = positions.copy()
        positions.clear()
        for pos in pos_copy:
            for x in range(-self.update_distance, self.update_distance +1):
                for y in range(-self.update_distance, self.update_distance +1):
                    chunk_pos = self.get_chunk_num(Vector(x, y)) + Vector(x, y)
                    positions.add(chunk_pos)

        for pos in positions:
            chunk_x, chunk_y = pos.tuple
            if chunk_x in self.__chunk_map and chunk_y in self.__chunk_map[chunk_x]:
                for actor_name in self.__chunk_map[chunk_x][chunk_y]:
                    sync_data = self.actors[actor_name].get_for_net_sync()
                    if sync_data:
                        actor_updates[actor_name] = (sync_data, pos)

        return actor_updates
    

    def get_destroyed(self):
        destroyed = []
        for actor in self.__actors_to_destroy:
            destroyed.append(self.actors.pop(actor.name).name)
        
        self.__actors_to_destroy.clear()
        return destroyed
        

    def tick(self, delta_time):
        self.__chunk_map.clear() 
        for actor in self.actors.values(): #* not optimal, but it will do for now
            self.__add_actor_to_chunk(actor)

        self.__physics_step(delta_time * self.simulation_speed)

        for widget in self.widgets.values():
            if widget.visible and issubclass(widget.__class__, Button):
                widget.tick(self.pressed_keys, Key.MOUSE_LEFT in self.released_keys, self.screen_mouse_pos)         #TODO fix this
        

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


    def __add_actor_to_chunk(self, actor):
        chunk_x, chunk_y = self.get_chunk_num(actor.position)
        if chunk_x not in self.__chunk_map:
            self.__chunk_map[chunk_x] = {}
        if chunk_y not in self.__chunk_map[chunk_x]:
            self.__chunk_map[chunk_x][chunk_y] = set()
        self.__chunk_map[chunk_x][chunk_y].add(actor.name)
        
    #?endif

