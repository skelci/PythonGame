from components.datatypes import *
from components.material import Material



class Actor:
    def __init__(self, name, half_size, position = Vector(), visible = False, material = None, restitution = 1):
        self.name = name
        self.half_size = half_size
        self.position = position
        self.visible = visible
        self.material = material
        self.restitution = restitution


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
        if issubclass(value.__class__, Material):
            self.__material = value
        else:
            raise Exception("Material name must be a string:", value)
        

    @property
    def restitution(self):
        return self.__restitution
    

    @restitution.setter
    def restitution(self, value):
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            self.__restitution = value
        else:
            raise Exception("Restitution must be a float between 0 and 1:", value)


    def tick(self, delta_time):
        pass


    def on_collision(self, collision_data):
        pass


