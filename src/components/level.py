"""
This module contains the Level class, which is used to create a level in the game.
"""

from components.datatypes import *
from components.actor import Actor
from components.background import Background
from components.rigidbody import Rigidbody
from components.character import Character
from components.game_math import *



class Level:
    """
    This class represents a level in the game. It contains all the actors and handles the physics simulation.
    It also handles the chunk system for efficient actor management.
    """


    def __init__(self, name: str, default_character: Character, actors: list[Actor] = [], background: Background = None, simulation_speed = 1, gravity = 1):
        """
        Args:
            name: Name of the level.
            default_character: Default character for the level. It will be used to create a new character when the player spawns in the level.
            actors: List of actors to be added to the level.
            background: Background for the level. It will be used to render the background.
            simulation_speed: Speed of the physics simulation. 1 is normal.
            gravity: Gravity scale for the level. 1 is normal.
        """
        self.__engine_ref = None

        self.name = name
        self.default_character = default_character
        self.background = background
        self.simulation_speed = simulation_speed
        self.gravity = gravity

        self.__actors = {}
        self.__rigidbodies = {}
        self.__actors_with_overlap_events = {}
        self.__chunks = {}
        self.__actors_to_destroy = set()
        self.__actors_to_create = set()

        for actor in actors:
            self.register_actor(actor)


    @property
    def engine_ref(self):
        """
        ServerEngine | ClientEngine - Reference to the engine that created this level.
        """
        return self.__engine_ref
    

    @engine_ref.setter
    def engine_ref(self, value):
        if value.__class__.__name__ == "ServerEngine" or value.__class__.__name__ == "ClientEngine":
            self.__engine_ref = value
        else:
            raise TypeError("Engine refrence must be a Engine object:", value)


    @property
    def name(self):
        """
        str - Name of the level.
        """
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string:", value)
        

    @property
    def default_character(self):
        """
        Character - Default character for the level. It will be used to create a new character when the player spawns in the level.
        """
        return self.__default_character
    

    @default_character.setter
    def default_character(self, value):
        if issubclass(value, Character):
            self.__default_character = value
        else:
            print(value.__class__)
            raise TypeError("Default character must be a subclass of Character:", value)


    @property
    def background(self):
        """
        Background - Background for the level. It will be used to render the background.
        """
        return self.__background
    

    @background.setter
    def background(self, value):
        if isinstance(value, str) or value is None:
            self.__background = value
        else:
            raise TypeError("Background must be a string or None:", value)
        

    @property
    def actors(self):
        """
        dict[str, Actor] - Dictionary of all actors in the level. The key is the actor's name and the value is the actor object.
        """
        return self.__actors
    

    @property
    def rigidbodies(self):
        """
        dict[str, Rigidbody] - Dictionary of all rigidbodies in the level. The key is the actor's name and the value is the actor object.
        """
        return self.__rigidbodies
    

    @property
    def simulation_speed(self):
        """
        float - Speed of the physics simulation. 1 is normal.
        """
        return self.__simulation_speed
    

    @simulation_speed.setter
    def simulation_speed(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__simulation_speed = value
        else:
            raise TypeError("Simulation speed must be a positive number:", value)
        

    @property
    def gravity(self):
        """
        float - Gravity scale for the level. 1 is normal.
        """
        return self.__gravity
    

    @gravity.setter
    def gravity(self, value):
        if isinstance(value, (int, float)):
            self.__gravity = value
        else:
            raise TypeError("Gravity must be a float:", value)
        

    @property
    def chunks(self):
        """
        dict[int, dict[int, set[str]]] - Dictionary of all chunks in the level. The key is the chunk's x and y coordinates and the value is a set of actor names in that chunk.
        """
        return self.__chunks
        

    def register_actor(self, actor: Actor):
        """
        Adds an actor to the level. The actor will be added to the level in the next tick.
        Args:
            actor: Actor to be added to the level.
        Raises:
            TypeError: If the actor is not a subclass of Actor.
        """
        if isinstance(actor, Actor):
            actor.engine_ref = self.engine_ref
            actor.level_ref = self
            self.__actors_to_create.add(actor)
        else:
            raise TypeError("Actor must be a subclass of Actor:", actor)
        

    def destroy_actor(self, actor: Actor):
        """
        Marks an actor for destruction. The actor will be removed from the level in the next tick.
        Args:
            actor: Actor to be destroyed.
        Raises:
            ValueError: If the actor is not in the level.
        """
        if actor.name in self.actors:
            self.__actors_to_destroy.add(actor)
        else:
            raise ValueError("Actor not found in level:", actor)


    def get_new_actors(self):
        """
        Called only by the engine.
        Returns a list of actors that were added to the level in the last tick.
        """
        new_actors = []
        actors_to_create = self.__actors_to_create.copy()
        for actor in actors_to_create:
            actor.engine_ref = self.engine_ref
            actor.level_ref = self
            self.actors[actor.name] = actor
            if isinstance(actor, Rigidbody):
                self.rigidbodies[actor.name] = actor
            if actor.generate_overlap_events:
                self.__actors_with_overlap_events[actor.name] = actor
            if actor.visible:
                new_actors.append(actor)
            self.add_actor_to_chunk(actor)

        self.__actors_to_create.clear()
        return new_actors
    

    def get_destroyed(self):
        """
        Called only by the engine.
        Returns a list of actors that were destroyed in the last tick.
        """
        destroyed = []
        actors_to_destroy = self.__actors_to_destroy.copy()
        for actor in actors_to_destroy:
            destroyed.append(self.actors.pop(actor.name))
            if isinstance(actor, Rigidbody):
                self.rigidbodies.pop(actor.name)
            if actor.name in self.__actors_with_overlap_events:
                self.__actors_with_overlap_events.pop(actor.name)
            chk_x, chk_y = actor.chunk
            self.chunks[chk_x][chk_y].remove(actor.name)
        
        self.__actors_to_destroy.clear()
        return destroyed
    

    def get_actors_in_chunks_3x3(self, chunk_pos: Vector):
        """
        Returns a list of actors in the 3x3 chunks around the given chunk position.
        Args:
            chunk_pos: Position of the chunk.
        Returns:
            list[Actor] - List of actors in the 3x3 chunks around the given chunk position.
        """
        actors = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                chunk_x, chunk_y = chunk_pos + Vector(x, y)
                if chunk_x not in self.__chunks or chunk_y not in self.__chunks[chunk_x]:
                    continue
                for actor_name in self.__chunks[chunk_x][chunk_y]:
                    actors.append(self.actors[actor_name])

        return actors
    

    def add_actor_to_chunk(self, actor):
        """
        Called only by the engine.
        Adds an actor to the chunk system.
        """
        chunk_x, chunk_y = get_chunk_cords(actor.position)
        if chunk_x not in self.__chunks:
            self.__chunks[chunk_x] = {}
        if chunk_y not in self.__chunks[chunk_x]:
            self.__chunks[chunk_x][chunk_y] = set()
        self.__chunks[chunk_x][chunk_y].add(actor.name)

        actor.chunk = Vector(chunk_x, chunk_y)


    #?ifdef SERVER
    def get_updates(self, players):
        """
        Called only by the engine.
        Returns a dictionary of actors that need to be updated for the given players.
        """
        chunk_updates = {}

        for chunk in self.get_loaded_chunks(players):
            chunk_x, chunk_y = chunk
            if chunk_x not in self.__chunks or chunk_y not in self.__chunks[chunk_x]:
                continue

            for actor_name in self.__chunks[chunk_x][chunk_y]:
                sync_data = self.actors[actor_name].get_for_net_sync()
                if not sync_data:
                    continue

                actor = self.actors[actor_name]
                if "position" in sync_data:
                    a_chk_x, a_chk_y = actor.chunk
                    if (a_chk_x != chunk_x or a_chk_y != chunk_y) and actor_name in self.__chunks[a_chk_x][a_chk_y]:
                        self.__chunks[a_chk_x][a_chk_y].remove(actor_name)
                        self.add_actor_to_chunk(actor)
                        
                if not actor.visible and "visible" not in sync_data:
                    continue 
                if "visible" in sync_data:
                    del sync_data["visible"]

                if chunk_x not in chunk_updates:
                    chunk_updates[chunk_x] = {}
                if chunk_y not in chunk_updates[chunk_x]:
                    chunk_updates[chunk_x][chunk_y] = {}
                chunk_updates[chunk_x][chunk_y][actor_name] = sync_data
                        
        return chunk_updates
        

    def get_loaded_chunks(self, players: list):
        """
        Returns a set of chunk positions that are updated for the given players.
        Args:
            players: List of players to get the loaded chunks for. Player is an object with a position and previous_different_chunk attributes.
        Returns:
            set[Vector] - Set of chunk positions that are updated for the given players.
        """
        chunks = set()
        for player in players:
            for x in range(-player.update_distance, player.update_distance + 1):
                for y in range(-player.update_distance, player.update_distance + 1):
                    chunk_pos = get_chunk_cords(player.position) + Vector(x, y)
                    previous_chunk_pos = player.previous_different_chunk + Vector(x, y)
                    chunks.add(chunk_pos)
                    chunks.add(previous_chunk_pos)

        return chunks
        

    def tick(self, delta_time: float):
        """
        Called every tick by the engine.
        Updates the level and all actors in the level.
        Args:
            delta_time: Time since the last engine tick.
        """
        delta_time *= self.simulation_speed
        
        for actor in self.actors.values():
            actor.tick(delta_time)
                
        max_iterations = 8
        collisions_not_resolved = True
        collided_actors = {}

        while collisions_not_resolved and max_iterations > 0:
            collisions_not_resolved = False
            corrected_actors = {}

            for actor1 in self.rigidbodies.values():
                if not actor1.simulate_physics:
                    continue

                for actor2 in self.get_actors_in_chunks_3x3(get_chunk_cords(actor1.position)):
                    if actor2 is actor1 or not actor2.collidable:
                        continue

                    if actor1.position.distance(actor2.position) > actor1.half_size.abs.max + actor2.half_size.abs.max:
                        continue
                    direction = actor1.collision_response_direction(actor2)
                    if direction == Vector(0, 0):
                        continue

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
        for actor1 in self.rigidbodies.values():
            if not actor1.simulate_physics:
                continue

            for actor2 in self.get_actors_in_chunks_3x3(get_chunk_cords(actor1.position)):
                if actor2 is actor1 or not actor2.collidable:
                    continue

                actor1.half_size += KINDA_SMALL_NUMBER
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
                actor1.half_size -= KINDA_SMALL_NUMBER

        for name, direction in collided_actors_directions.items():
            self.actors[name].collided_sides = direction

        overlaped_actors = {}
        for actor1 in self.__actors_with_overlap_events.values():
            actor1.half_size += KINDA_SMALL_NUMBER
            for actor2 in self.get_actors_in_chunks_3x3(get_chunk_cords(actor1.position)):
                if actor1 is actor2 or not is_overlapping_rect(actor1, actor2):
                    continue

                if actor2.name not in overlaped_actors:
                    overlaped_actors[actor2.name] = set()
                overlaped_actors[actor2.name].add(actor1)

            actor1.half_size -= KINDA_SMALL_NUMBER

        for actor_name, overlaped_set in overlaped_actors.items():
            for actor in overlaped_set - self.actors[actor_name].previously_collided:
                self.actors[actor_name].on_overlap_begin(actor)
            for actor in self.actors[actor_name].previously_collided - overlaped_set:
                self.actors[actor_name].on_overlap_end(actor)

        for actor_name, overlaped_set in overlaped_actors.items():
            self.actors[actor_name].previously_collided = overlaped_set

    #?endif
        

