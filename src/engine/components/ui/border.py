#?attr CLIENT

"""
This module contains the Border class, which is used to create a border widget.
"""

from .widget import Widget
from engine.datatypes import *

import pygame



class Border(Widget):
    """
    Represents a border widget. It is a colored rectangle with a specified border color and thickness.
    """

    def __init__(self, name: str, position: Vector, size: Vector, layer = 0, border_color: Color = Color(255, 255, 255), bg_color: Color = Color(0, 0, 0, 0), visible = False, thickness = 10, subwidgets: dict[str, Widget] = {}, subwidget_offsets: dict[str, Vector] = {}, subwidget_alignments: dict[str, Alignment] = {}, update_interval = 1):
        """
        Refer to the Widget class for more information about the parameters.
        Args:
            bg_color: Background color of the border. Default is Color(0, 0, 0, 0).
            border_color: Color of the border. Default is Color(255, 255, 255).
            thickness: Thickness of the border. Default is 10.
        """
        super().__init__(name, position, size, bg_color, layer, visible, subwidgets, subwidget_offsets, subwidget_alignments, update_interval)

        self.border_color = border_color
        self.thickness = thickness


    @property
    def border_color(self):
        """ Color - Color of the border. """
        return self.__border_color
    

    @border_color.setter
    def border_color(self, value):
        if isinstance(value, Color):
            self.__border_color = value
            self.updated = False
        else:
            raise TypeError("Border color must be a Color:", value)


    @property
    def thickness(self):
        """ int - Thickness of the border. """
        return self.__thickness
    

    @thickness.setter
    def thickness(self, value):
        if isinstance(value, int) and 0 <= value <= min(*self.size):
            self.__thickness = value
            self.updated = False
        else:
            raise TypeError("Thickness must be an integer between 0 and the half of the smallest dimension of the widget:", value)
        

    @property
    def self_surface(self):
        """
        pygame.Surface - Surface of the border widget. This is a colored rectangle with a border.
        """
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.fill(self.color.tuple)
        pygame.draw.rect(surface, self.border_color.tuple, (0, 0, *self.size.tuple), self.thickness)

        return surface

