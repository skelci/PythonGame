from components.datatypes import *

import pygame



class Widget:
    def __init__(self, name, position, size, layer, color, visible = False):
        self.name = name
        self.position = position
        self.size = size
        self.layer = layer
        self.color = color
        self.visible = visible


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
    def position(self):
        return self.__position
    

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self.__position = value
        else:
            raise Exception("Position must be a Vector:", value)
        

    @property
    def size(self):
        return self.__size
    

    @size.setter
    def size(self, value):
        if isinstance(value, Vector):
            self.__size = value
        else:
            raise Exception("Size must be a Vector:", value)
        

    @property
    def layer(self):
        return self.__layer
    

    @layer.setter
    def layer(self, value):
        if isinstance(value, int):
            self.__layer = value
        else:
            raise Exception("Layer must be an int:", value)
        

    @property
    def color(self):
        return self.__color
    

    @color.setter
    def color(self, value):
        if isinstance(value, Color):
            self.__color = value
        else:
            raise Exception("Color must be a Color:", value)
        

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
    def surface(self):
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.fill(self.color.tuple)
        return surface
        
    