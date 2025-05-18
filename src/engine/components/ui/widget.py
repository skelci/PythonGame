#?attr CLIENT

"""
This module contains the Widget class, which is core to the GUI system.
"""

from engine.datatypes import *

import pygame
from OpenGL.GL import *



class Widget:
    """
    Core widget class for the GUI system. All positions and sizes are in pixels, based on resolution = Vector(1600, 900).
    This class is used to create a widget that can be displayed on the screen.
    It can be also used to easily position subwidgets relative to the parent widget.
    This widget is a colored rectangle.
    """
    
    def __init__(self, name: str, position: Vector, size: Vector, color: Color, layer = 0, visible = True, subwidgets: dict[str, 'Widget'] = {}, subwidget_offsets: dict[str, Vector] = {}, subwidget_alignments: dict[str, Alignment] = {}, update_interval = 1):
        """
        Args:
            name: Name of the widget.
            position: Position of the top left corner of the widget. Vector(0, 0) is the top left corner of the screen.
            size: Size of the widget.
            color: Color of the rectangle.
            layer: Layer of the widget. Higher layers are drawn on top of lower layers.
            visible: Whether the widget is visible or not. If not, it won't process even subwidgets.
            subwidgets: Dictionary of subwidgets. The key is the name of the subwidget and the value is the widget itself.
            subwidget_offsets: Dictionary of subwidget offsets. The key is the name of the subwidget and the value is offset, which tells where the subwidget is positioned relative to the parent widget and alignment.
            subwidget_alignments: Dictionary of subwidget alignments. The key is the name of the subwidget and the value is the alignment, which tells how the subwidget is aligned relative to the parent widget and offset (where will Vector(0, 0) be positioned).
            update_interval: Update interval for the widget. If the widget is updated, it will be updated after update_interval update calls. If widget is updated every frame, it can cause performance issues.
        """
        self._parent = None
        self.update_interval = update_interval
        self.__update_clock = 0

        self.name = name
        self.position = position
        self.size = size
        self.layer = layer
        self.color = color
        self.visible = visible
        self.subwidgets = subwidgets
        self.subwidget_offsets = subwidget_offsets
        self.subwidget_alignments = subwidget_alignments

        self.__surface_id = None
        self.subwidget_updated = False
        self.__updated = False


    @property
    def update_interval(self):
        """ int - Update interval for the widget. """
        return self.__update_interval
    

    @update_interval.setter
    def update_interval(self, value):
        if isinstance(value, int) and value > 0:
            self.__update_interval = value
        else:
            raise TypeError("Update interval must be a positive int:", value)


    @property
    def name(self):
        """ str - Name of the widget. """
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string:", value)
        

    @property
    def position(self):
        """ Vector - Position of the top left corner of the widget. """
        return self.__position
    

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self.__position = value
        else:
            raise TypeError("Position must be a Vector:", value)
        

    @property
    def size(self):
        """ Vector - Size of the widget. """
        return self.__size
    

    @size.setter
    def size(self, value):
        if isinstance(value, Vector):
            self.__size = value
            self.updated = False
        else:
            raise TypeError("Size must be a Vector:", value)
        

    @property
    def layer(self):
        """ int - Layer of the widget. Higher layers are drawn on top of lower layers. """
        return self.__layer
    

    @layer.setter
    def layer(self, value):
        if isinstance(value, int):
            self.__layer = value
        else:
            raise TypeError("Layer must be an int:", value)
        

    @property
    def color(self):
        """ Color - Color of the widget rectangle. """
        return self.__color
    

    @color.setter
    def color(self, value):
        if isinstance(value, Color):
            self.__color = value
            self.updated = False
        else:
            raise TypeError("Color must be a Color:", value)
        

    @property
    def visible(self):
        """ bool - Whether the widget is visible or not. If not, it won't process even subwidgets. """
        return self.__visible
    

    @visible.setter
    def visible(self, value):
        if isinstance(value, bool):
            self.__visible = value
        else:
            raise TypeError("Visible must be a bool:", value)


    @property
    def subwidgets(self):
        """ dict[str, Widget] - Dictionary of subwidgets. The key is the name of the subwidget and the value is the widget itself. """
        return self.__subwidget
    

    @subwidgets.setter
    def subwidgets(self, value):
        if isinstance(value, dict):
            self.__subwidget = value
            for widget in value.values():
                if not isinstance(widget, Widget):
                    raise TypeError("Subwidget must be a Widget:", widget)
                widget._parent = self
        else:
            raise TypeError("Subwidget must be a dict of Widgets:", value)


    @property
    def updated(self):
        """ bool - Whether the widget is updated or not. """
        return self.__updated
    

    @updated.setter
    def updated(self, value):
        if isinstance(value, bool):
            self.__update_clock += 1
            if self.__update_clock >= self.__update_interval:
                self.__update_clock = 0
                self.__updated = value
                if not value and self._parent:
                    self._parent.subwidget_updated = False
        else:
            raise TypeError("Updated must be a bool:", value)
        

    @property
    def subwidget_updated(self):
        """ bool - Whether the subwidget is updated or not. """
        return self.__subwidget_updated
    

    @subwidget_updated.setter
    def subwidget_updated(self, value):
        if isinstance(value, bool):
            self.__subwidget_updated = value
            if not value and self._parent:
                self._parent.subwidget_updated = False
        else:
            raise TypeError("Subwidget updated must be a bool:", value)
        

    @property
    def subwidget_offsets(self):
        """ dict[str, Vector] - Dictionary of subwidget offsets. The key is the name of the subwidget and the value is offset, which tells where the subwidget is positioned relative to the parent widget and alignment. """
        return self.__subwidget_offset


    @subwidget_offsets.setter
    def subwidget_offsets(self, value):
        if isinstance(value, dict):
            self.__subwidget_offset = value
        else:
            raise TypeError("Subwidget offset must be a dict of Vectors:", value)
        

    @property
    def subwidget_alignments(self):
        """ dict[str, Alignment] - Dictionary of subwidget alignments. The key is the name of the subwidget and the value is the alignment, which tells how the subwidget is aligned relative to the parent widget and offset (where will Vector(0, 0) be positioned). """
        return self.__subwidget_alignment
    

    @subwidget_alignments.setter
    def subwidget_alignments(self, value):
        if isinstance(value, dict):
            self.__subwidget_alignment = value
        else:
            raise TypeError("Subwidget alignment must be a dict of Aligments:", value)
        

    @property
    def self_surface(self):
        """ pygame.Surface - Surface of the widget. This is a colored rectangle. """
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.fill(self.color.tuple)
        return surface


    @property
    def surface(self):
        """ pygame.Surface - Surface of the widget combined with subwidgets. """
        if self.updated and self.subwidget_updated:
            return self.__combined_surface

        if self.updated:
            surface = self._surface
        else:
            surface = self.self_surface
            self._surface = surface

        self.__combined_surface = surface.copy()
        if not self.subwidgets:
            self.subwidget_updated = True
            self.updated = True
            return self.__combined_surface

        if not self.subwidget_updated or not self.updated:
            sorted_widgets = sorted(list(self.subwidgets.keys()), key=lambda x: self.subwidgets[x].layer)
            for widget in sorted_widgets:
                self.__combined_surface.blit(self.subwidgets[widget].surface, self.subwidget_pos(widget).tuple)

        self.subwidget_updated = True
        self.updated = True

        return self.__combined_surface
    

    def subwidget_pos(self, widget: str) -> Vector:
        """
        Calculate the position of a subwidget relative to the parent widget.
        Args:
            widget: Name of the subwidget.
        Returns:
            Vector - Position of the top left corner of the subwidget relative to the parent widget.
        """
        offset, alignment = self.subwidget_offsets[widget], self.subwidget_alignments[widget]
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
    

    def create_material(self):
        """ Creates an OpenGL texture from the widget surface. """
        surface_id = self.__surface_id
        if surface_id is not None:
            glDeleteTextures(1, [surface_id])
        
        surface = self.surface

        surface_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, surface_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        width, height = surface.get_size()
        image_data = pygame.image.tostring(surface, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.__surface_id = surface_id


    def use_material(self):
        """ Use the OpenGL texture for rendering. """
        if not self.subwidget_updated or not self.updated or self.__surface_id is None:
            self.create_material()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.__surface_id)
        


