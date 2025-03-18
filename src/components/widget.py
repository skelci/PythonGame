from components.datatypes import *
from engine.gl_wrapper import *

import pygame



class Widget:
    def __init__(self, name, position, size, color, layer = 0, visible = False, subwidget = None, subwidget_offset = Vector(), subwidget_alignment = Alignment.CENTER):
        self.name = name
        self.position = position
        self.size = size
        self.layer = layer
        self.color = color
        self.visible = visible
        self.subwidget = subwidget
        self.subwidget_offset = subwidget_offset

        self.__tex_id = None
        if subwidget:
            subwidget.load_texture = False            


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
    def subwidget(self):
        return self.__subwidget
    

    @subwidget.setter
    def subwidget(self, value):
        if value is None or isinstance(value, Widget):
            self.__subwidget = value
        else:
            raise TypeError("Subwidget must be a Widget:", value)
        

    @property
    def subwidget_offset(self):
        return self.__subwidget_offset


    @subwidget_offset.setter
    def subwidget_offset(self, value):
        if isinstance(value, Vector):
            self.__subwidget_offset = value
        else:
            raise TypeError("Subwidget offset must be a Vector:", value)


    @property
    def tex_id(self):
        return self.__tex_id


    @property
    def surface(self):
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.fill(self.color.tuple)

        if self.subwidget:
            surface.blit(self.subwidget.surface, self.subwidget_pos.tuple)

        return surface
    

    @property
    def subwidget_pos(self):
        subwidget_offset = self.subwidget_offset

        if not self.subwidget:
            return subwidget_offset
        
        if self.subwidget_alignment in (Alignment.TOP_CENTER, Alignment.CENTER, Alignment.BOTTOM_CENTER):
            subwidget_offset.x += (self.size.x - self.subwidget.size.x) / 2
        
        if self.subwidget_alignment in (Alignment.TOP_RIGHT, Alignment.CENTER_RIGHT, Alignment.BOTTOM_RIGHT):
            subwidget_offset.x += self.size.x - self.subwidget.size.x

        if self.subwidget_alignment in (Alignment.LEFT_CENTER, Alignment.CENTER, Alignment.RIGHT_CENTER):
            subwidget_offset.y += (self.size.y - self.subwidget.size.y) / 2

        if self.subwidget_alignment in (Alignment.BOTTOM_LEFT, Alignment.BOTTOM_CENTER, Alignment.BOTTOM_RIGHT):
            subwidget_offset.y += self.size.y - self.subwidget.size.y

        return subwidget_offset


    def draw(self, bottom_left, size):
        if self.visible and self.tex_id:
            if self.load_texture and not self.__tex_id:
                self.__tex_id = GLWrapper.load_texture(self.surface)
            GLWrapper.draw_texture(self.tex_id, *bottom_left, *size)
        
    