#?attr CLIENT

"""
Core widget class for the GUI system.
"""

from components.datatypes import *

import pygame



class Widget:
    """
    Core widget class for the GUI system. All positions and sizes are in pixels, based on resolution = Vector(1600, 900).
    This class is used to create a widget that can be displayed on the screen.
    It can be also used to easily position subwidgets relative to the parent widget.
    This widget is a colored rectangle.
    """
    
    
    def __init__(self, name: str, position: Vector, size: Vector, color: Color, layer = 0, visible = True, subwidgets: dict[str, 'Widget'] = {}, subwidget_offsets: dict[str, Vector] = {}, subwidget_alignments: dict[str, Alignment] = {}):
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
        """
        self.name = name
        self.position = position
        self.size = size
        self.layer = layer
        self.color = color
        self.visible = visible
        self.subwidgets = subwidgets
        self.subwidget_offsets = subwidget_offsets
        self.subwidget_alignments = subwidget_alignments


    @property
    def name(self):
        """
        str - Name of the widget.
        """
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string:", value)
        

    @property
    def position(self):
        """
        Vector - Position of the top left corner of the widget.
        """
        return self.__position
    

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self.__position = value
        else:
            raise TypeError("Position must be a Vector:", value)
        

    @property
    def size(self):
        """
        Vector - Size of the widget.
        """
        return self.__size
    

    @size.setter
    def size(self, value):
        if isinstance(value, Vector):
            self.__size = value
            self._updated = False
        else:
            raise TypeError("Size must be a Vector:", value)
        

    @property
    def layer(self):
        """
        int - Layer of the widget. Higher layers are drawn on top of lower layers.
        """
        return self.__layer
    

    @layer.setter
    def layer(self, value):
        if isinstance(value, int):
            self.__layer = value
        else:
            raise TypeError("Layer must be an int:", value)
        

    @property
    def color(self):
        """
        Color - Color of the widget rectangle.
        """
        return self.__color
    

    @color.setter
    def color(self, value):
        if isinstance(value, Color):
            self.__color = value
            self._updated = False
        else:
            raise TypeError("Color must be a Color:", value)
        

    @property
    def visible(self):
        """
        bool - Whether the widget is visible or not. If not, it won't process even subwidgets.
        """
        return self.__visible
    

    @visible.setter
    def visible(self, value):
        if isinstance(value, bool):
            self.__visible = value
        else:
            raise TypeError("Visible must be a bool:", value)


    @property
    def subwidgets(self):
        """
        dict[str, Widget] - Dictionary of subwidgets. The key is the name of the subwidget and the value is the widget itself.
        """
        self._subwidget_updated = False
        return self.__subwidget
    

    @subwidgets.setter
    def subwidgets(self, value):
        if isinstance(value, dict):
            self.__subwidget = value
        else:
            raise TypeError("Subwidget must be a dict of Widgets:", value)
        

    @property
    def subwidget_offsets(self):
        """
        dict[str, Vector] - Dictionary of subwidget offsets. The key is the name of the subwidget and the value is offset, which tells where the subwidget is positioned relative to the parent widget and alignment.
        """
        self._subwidget_updated = False
        return self.__subwidget_offset


    @subwidget_offsets.setter
    def subwidget_offsets(self, value):
        if isinstance(value, dict):
            self.__subwidget_offset = value
        else:
            raise TypeError("Subwidget offset must be a dict of Vectors:", value)
        

    @property
    def subwidget_alignments(self):
        """
        dict[str, Alignment] - Dictionary of subwidget alignments. The key is the name of the subwidget and the value is the alignment, which tells how the subwidget is aligned relative to the parent widget and offset (where will Vector(0, 0) be positioned).
        """
        self._subwidget_updated = False
        return self.__subwidget_alignment
    

    @subwidget_alignments.setter
    def subwidget_alignments(self, value):
        if isinstance(value, dict):
            self.__subwidget_alignment = value
        else:
            raise TypeError("Subwidget alignment must be a dict of Aligments:", value)


    @property
    def surface(self):
        """
        pygame.Surface - Surface of the widget. This is a colored rectangle.
        """
        if self._updated and self._subwidget_updated:
            return self.__combined_surface
        
        if not self._updated:
            surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
            surface.fill(self.color.tuple)
            self.__surface = surface
            self._updated = True

        self.__combined_surface = self.__surface.copy()
        if not self.subwidgets:
            self._subwidget_updated = True
            return self.__combined_surface
        

        if not self._subwidget_updated:
            for widget in self.subwidgets.keys():
                self.__combined_surface.blit(self.subwidgets[widget].surface, self.subwidget_pos(widget).tuple)

        self._subwidget_updated = True

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


