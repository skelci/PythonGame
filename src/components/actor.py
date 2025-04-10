"""
This module contains the Actor class, which is used to create an objects inside the level.
"""

from components.datatypes import *
from components.material import Material


class Actor:
    """
    This class represents an actor in the game. It is used to create an object that can be placed in the level.
    It can be used to create a static object, a dynamic object or a trigger.
    """


    def __init__(self, name: str, position: Vector, half_size = Vector(0.5, 0.5), generate_overlap_events = False, collidable = True, visible = True, material: Material = None, render_layer = 0, restitution = 1):
        """
        Args:
            name: Name of the actor.
            position: Position of the center of the actor.
            half_size: Half size of the actor. This is used to scale material and collision box.
            generate_overlap_events: Whether to generate overlap events or not. If true, the actor will generate overlap events when it overlaps with another actor.
            collidable: Whether the actor is collidable or not. If true, the actor will collide with other actors.
            visible: Whether the actor is visible or not. If true, the actor will be rendered.
            material: Material of the actor. This is used to render the actor.
            render_layer: Render layer of the actor. Higher layers are rendered on top of lower layers.
            restitution: Restitution of the actor. This is used to calculate the bounce of the actor when it collides with another actor.
        """
        self.__outdated = {
            "half_size": False,
            "position": False,
            "visible": False,
            "material": False,
        }

        self.__engine_ref = None
        self.__level_ref = None
        self.name = name
        self.half_size = half_size
        self.position = position
        self.generate_overlap_events = generate_overlap_events
        self.collidable = collidable
        self.material = material
        self.visible = visible
        self.restitution = restitution
        self.render_layer = render_layer

        self.previously_collided = set()

        for k, v in self.__outdated.items():
            if v:
                self.__outdated[k] = False



    @property
    def engine_ref(self):
        """
        ServerEngine or ClientEngine - Reference to the engine that created this actor.
        """
        return self.__engine_ref
    

    @engine_ref.setter
    def engine_ref(self, value):
        if value.__class__.__name__ == "ServerEngine" or value.__class__.__name__ == "ClientEngine":
            self.__engine_ref = value
        else:
            raise TypeError("Engine refrence must be a Engine object:", value)
        

    @property
    def level_ref(self):
        """
        Level - Reference to the level, in which this actor is placed.
        """
        return self.__level_ref
    

    @level_ref.setter
    def level_ref(self, value):
        if any("Level" == cls.__name__ for cls in value.__class__.__mro__):
            self.__level_ref = value
        else:
            raise TypeError("Level refrence must be a Level object:", value)


    @property
    def name(self):
        """
        str - Name of the actor.
        """
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string:", value)


    @property
    def half_size(self):
        """
        Vector - Half size of the actor. This is used to scale material and collision box.
        """
        return self.__half_size
    

    @half_size.setter
    def half_size(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__half_size = value
            self.__outdated["half_size"] = True
        else:
            raise TypeError("Half size must be a Vector:", value)
        

    @property
    def position(self):
        """
        Vector - Position of the center of the actor.
        """
        return self.__position
    

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self.__position = value
            self.__outdated["position"] = True
        else:
            raise TypeError("Position must be a Vector:", value)
        

    @property
    def generate_overlap_events(self):
        """
        bool - Whether to generate overlap events or not. If true, the actor will generate overlap events when it overlaps with another actor.
        """
        return self.__generate_overlap_events
    

    @generate_overlap_events.setter
    def generate_overlap_events(self, value):
        if isinstance(value, bool):
            self.__generate_overlap_events = value
        else:
            raise TypeError("Generate overlap events must be a bool:", value)
        

    @property
    def collidable(self):
        """
        bool - Whether the actor is collidable or not. If true, the actor will collide with other actors.
        """
        return self.__collidable
    

    @collidable.setter
    def collidable(self, value):
        if isinstance(value, bool):
            self.__collidable = value
        else:
            raise TypeError("Simulate physics must be a bool:", value)
        

    @property
    def visible(self):
        """
        bool - Whether the actor is visible or not. If true, the actor will be rendered.
        """
        return self.__visible
    

    @visible.setter
    def visible(self, value):
        if isinstance(value, bool):
            if not self.material and value:
                raise ValueError("Material must be set to use visible:", value)
            self.__visible = value
            self.__outdated["visible"] = True
        else:
            raise TypeError("Visible must be a bool:", value)
        

    @property
    def material(self):
        """
        Material - Material of the actor. This is used to render the actor.
        """
        return self.__material
    

    @material.setter
    def material(self, value):
        if isinstance(value, Material) or value == None:
            self.__material = value
            self.__outdated["material"] = True
        else:
            raise TypeError("Material name must be a string or None:", value)
        

    @property
    def render_layer(self):
        """
        int - Render layer of the actor. Higher layers are rendered on top of lower layers.
        """
        return self.__render_layer
    

    @render_layer.setter
    def render_layer(self, value):
        if isinstance(value, int):
            self.__render_layer = value
        else:
            raise TypeError("Render layer must be an int:", value)
        

    @property
    def restitution(self):
        """
        float - Restitution of the actor. This is used to calculate the bounce of the actor when it collides with another actor.
        """
        return self.__restitution
    

    @restitution.setter
    def restitution(self, value):
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            self.__restitution = value
        else:
            raise TypeError("Restitution must be a float between 0 and 1:", value)
        

    @property
    def previously_collided(self):
        """
        set[Actor] - Set of actors that this actor has previously collided with.
        """
        return self.__previously_collided
    

    @previously_collided.setter
    def previously_collided(self, value):
        if isinstance(value, set):
            self.__previously_collided = value
        else:
            raise TypeError("Previously collided must be a set:", value)
        

    #?ifdef CLIENT
    def update_from_net_sync(self, data):
        """
        Called only inside the engine. This function is used to update the actor from the network sync data.
        """
        for key in data:
            match key:
                case "half_size":
                    self.half_size = Vector(*data[key])
                case "position":
                    self.position = Vector(*data[key])
                case "material":
                    self.material = self.engine_ref.get_material(data[key])
    #?endif
    

    #?ifdef SERVER
    def get_for_net_sync(self):
        """
        Called only inside the engine. This function is used to get the actor data which changed and needs to be synced with the client.
        """
        out = {}
        for key in self.__outdated:
            if self.__outdated[key]:
                if key == "material":
                    out[key] = self.material.name if self.material else None
                out[key] = getattr(self, key)
                self.__outdated[key] = False

        return out
        

    def get_for_full_net_sync(self):
        """
        Returns the all data of the actor to register it on the client.
        Returns:
            list[str, str, Vector] - List of all data of the actor. First element is the class name, second is the name of the actor, third is the position of the actor.
        """
        for key in self.__outdated:
            self.__outdated[key] = False
        return [
            self.__class__.__name__,
            self.name,
            self.position,
        ]


    def tick(self, delta_time: float):
        """
        It is called every engine tick.
        Args:
            delta_time: Time since the last tick in engine.
        """
        pass


    def on_collision(self, collision_data: CollisionData):
        """
        Called when the actor collides with another actor. It is called every tick for each actor that is colliding with this actor.
        Args:
            collision_data: Data of collision and other actor which is colliding with this actor. You can find definitions of this class in the datatypes module.
        """
        pass


    def on_overlap_begin(self, other_actor: 'Actor'):
        """
        Called when the actor overlaps with another actor. It is called only once when the overlap begins for each actor that is overlapping with this actor.
        Args:
            other_actor: Actor which is overlapping with this actor.
        """
        pass


    def on_overlap_end(self, other_actor: 'Actor'):
        """
        Called when the actor stops overlapping with another actor. It is called only once when the overlap ends for each actor that is overlapping with this actor.
        Args:
            other_actor: Actor which is overlapping with this actor.
        """
        pass
    #?endif

    
    def __str__(self):
        return self.name
    

    def __repr__(self):
        return self.__str__()
    

    def __hash__(self):
        return hash(self.name)
    

    def __eq__(self, other):
        if isinstance(other, Actor):
            return self.name == other.name
        return False


