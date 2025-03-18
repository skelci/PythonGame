from components.datatypes import *
from engine.gl_wrapper import *

import pygame



class Widget:
    def __init__(self, name, position, size, color, layer = 0, visible = False, load_texture = True):
        self.name = name
        self.position = position
        self.size = size
        self.layer = layer
        self.color = color
        self.visible = visible

        self.__tex_id = None
        if load_texture:
            self.__tex_id = GLWrapper.load_texture(self.surface)


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
    def position(self):
        return self.__position
    

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self.__position = value
        else:
            raise TypeError("Position must be a Vector:", value)
        

    @property
    def size(self):
        return self.__size
    

    @size.setter
    def size(self, value):
        if isinstance(value, Vector):
            self.__size = value
        else:
            raise TypeError("Size must be a Vector:", value)
        

    @property
    def layer(self):
        return self.__layer
    

    @layer.setter
    def layer(self, value):
        if isinstance(value, int):
            self.__layer = value
        else:
            raise TypeError("Layer must be an int:", value)
        

    @property
    def color(self):
        return self.__color
    

    @color.setter
    def color(self, value):
        if isinstance(value, Color):
            self.__color = value
        else:
            raise TypeError("Color must be a Color:", value)
        

    @property
    def visible(self):
        return self.__visible
    

    @visible.setter
    def visible(self, value):
        if isinstance(value, bool):
            self.__visible = value
        else:
            raise TypeError("Visible must be a bool:", value)


    @property
    def tex_id(self):
        return self.__tex_id


    @property
    def surface(self):
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.fill(self.color.tuple)
        return surface


    def draw(self, bottom_left, size):
        if self.visible and self.tex_id:
            GLWrapper.draw_texture(self.tex_id, *bottom_left, *size)
        
    