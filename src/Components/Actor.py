from components.datatypes import *
from components.material import Material


class Actor:
    def __init__(self, game_ref, name, half_size, position = Vector(), generate_overlap_events = False, collidable = True, visible = True, material = None, restitution = 1):
        self.game_ref = game_ref
        self.name = name
        self.half_size = half_size
        self.position = position
        self.generate_overlap_events = generate_overlap_events
        self.collidable = collidable
        self.visible = visible
        self.material = material
        self.restitution = restitution

        self.previously_collided = set()


    @property
    def game_ref(self):
        return self.__game_ref
    

    @game_ref.setter
    def game_ref(self, value):
        if value.__class__.__name__ == "Game":
            self.__game_ref = value
        else:
            raise Exception("Game refrence must be a Game object:", value)


    @property
    def name(self):
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise Exception("Name must be a string:", value)


    @property
    def half_size(self):
        return self.__half_size
    

    @half_size.setter
    def half_size(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__half_size = value
        else:
            raise Exception("Half size must be a Vector:", value)
        

    @property
    def position(self):
        return self.__position
    

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self.__position = value
        else:
            raise Exception("Position must be a Vector:", value)
        

    @property
    def generate_overlap_events(self):
        return self.__generate_overlap_events
    

    @generate_overlap_events.setter
    def generate_overlap_events(self, value):
        if isinstance(value, bool):
            self.__generate_overlap_events = value
        else:
            raise Exception("Generate overlap events must be a bool:", value)
        

    @property
    def collidable(self):
        return self.__collidable
    

    @collidable.setter
    def collidable(self, value):
        if isinstance(value, bool):
            self.__collidable = value
        else:
            raise Exception("Simulate physics must be a bool:", value)
        

    @property
    def visible(self):
        return self.__visible
    

    @visible.setter
    def visible(self, value):
        if isinstance(value, bool):
            self.__visible = value
        else:
            raise Exception("Visible must be a bool:", value)
        

    @property
    def material(self):
        return self.__material
    

    @material.setter
    def material(self, value):
        if issubclass(value.__class__, Material) or value == None:
            self.__material = value
        else:
            raise Exception("Material name must be a string None:", value)
        

    @property
    def restitution(self):
        return self.__restitution
    

    @restitution.setter
    def restitution(self, value):
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            self.__restitution = value
        else:
            raise Exception("Restitution must be a float between 0 and 1:", value)
        

    @property
    def previously_collided(self):
        return self.__previously_collided
    

    @previously_collided.setter
    def previously_collided(self, value):
        if isinstance(value, set):
            self.__previously_collided = value
        else:
            raise Exception("Previously collided must be a set:", value)


    def tick(self, delta_time):
        pass


    def on_collision(self, collision_data):
        pass


    def on_overlap_begin(self, other_actor):
        pass


    def on_overlap_end(self, other_actor):
        pass

    
    def __str__(self):
        return self.name
    


