from components.datatypes import *

import os



class Actor:
    def __init__(self, name, half_size, position = Vector(), visible = True, texture = None):
        self.name = name
        self.half_size = half_size
        self.position = position
        self.visible = visible
        self.texture = texture


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
    def texture(self):
        return self.__texture
    

    @texture.setter
    def texture(self, value):
        if (isinstance(value, str) and os.path.isfile(value)) or value == None:
            self.__texture = value
        else:
            raise Exception("Texture must be a string:", value)
        

    def tick(self, delta_time):
        pass


