#?attr CLIENT
from components.datatypes import *
from engine.gl_wrapper import *

import pygame



class Widget:
    def __init__(self, name, position, size, color, layer=0, visible = True, subwidgets={}, subwidgets_offsets={}, subwidgets_alignments={}):
        self.__subwidget_is_text = {}
        self.__tex_id = None

        self.name = name
        self.position = position
        self.size = size
        self.layer = layer
        self.color = color
        self.visible = visible
        self.subwidgets = subwidgets
        self.subwidgets_offsets = subwidgets_offsets
        self.subwidgets_alignments = subwidgets_alignments


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
    def subwidgets(self):
        return self.__subwidget
    

    @subwidgets.setter
    def subwidgets(self, value):
        if isinstance(value, dict):
            self.__subwidget = value
            for name, x in value.items():
                if x is not None and hasattr(x, '__class__') and any(cls.__name__ == "Text" for cls in x.__class__.__mro__):
                    self.__subwidget_is_text[name] = True
                else:
                    self.__subwidget_is_text[name] = False
        else:
            raise TypeError("Subwidget must be a dict of Widgets:", value)
        

    @property
    def subwidgets_offsets(self):
        return self.__subwidget_offset


    @subwidgets_offsets.setter
    def subwidgets_offsets(self, value):
        if isinstance(value, dict):
            self.__subwidget_offset = value
        else:
            raise TypeError("Subwidget offset must be a dict of Vectors:", value)
        

    @property
    def subwidgets_alignments(self):
        return self.__subwidget_alignment
    

    @subwidgets_alignments.setter
    def subwidgets_alignments(self, value):
        if isinstance(value, dict):
            self.__subwidget_alignment = value
        else:
            raise TypeError("Subwidget alignment must be a dict of Aligments:", value)


    @property
    def tex_id(self):
        return self.__tex_id


    @property
    def surface(self):
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.fill(self.color.tuple)

        if not self.subwidgets:
            return surface
        
        for widget in self.subwidgets.keys():
            if self.__subwidget_is_text[widget]:
                continue
            surface.blit(self.subwidgets[widget].surface, self.subwidget_pos(widget).tuple)


        return surface
    

    def subwidget_pos(self, widget):
        offset, alignment = self.subwidgets_offsets[widget], self.subwidgets_alignments[widget]
        subwidget = self.subwidgets[widget]
        subwidget_offset = offset.copy

        if alignment in (Alignment.TOP_CENTER, Alignment.CENTER, Alignment.BOTTOM_CENTER):
            subwidget_offset.x += (self.size.x - subwidget.size.x) / 2
        
        if alignment in (Alignment.TOP_RIGHT, Alignment.CENTER_RIGHT, Alignment.BOTTOM_RIGHT):
            subwidget_offset.x += self.size.x - subwidget.size.x

        if alignment in (Alignment.CENTER_LEFT, Alignment.CENTER, Alignment.CENTER_RIGHT):
            subwidget_offset.y += (self.size.y - subwidget.size.y) / 2

        if alignment in (Alignment.BOTTOM_LEFT, Alignment.BOTTOM_CENTER, Alignment.BOTTOM_RIGHT):
            subwidget_offset.y += self.size.y - subwidget.size.y

        return subwidget_offset


    def draw(self, bottom_left, size):
        if self.visible:
            if not self.__tex_id:
                self.__tex_id = GLWrapper.load_texture(self.surface)
            GLWrapper.draw_texture(self.tex_id, *bottom_left, *size)

            for widget in self.subwidgets:
                if self.__subwidget_is_text[widget]:
                    self.subwidgets[widget].update_size()
                    self.subwidgets[widget].draw(bottom_left + self.subwidget_pos(widget), size / self.size)


