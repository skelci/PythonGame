#?attr CLIENT

"""
This module contains the Icon class, which is used to create an icon for the GUI system.
"""

from .widget import Widget

from engine.components.material import Material
from engine.datatypes import *

import pygame



class Icon(Widget):
    """ Represents an icon widget. It renders an icon on the screen using a specified image. """
    
    def __init__(self, name, position, size, material, layer=0, visible=True, subwidgets = {}, subwidget_offsets = {}, subwidget_alignments = {}):
        """
        For more information about the parameters, refer to the Widget class.
        Args:
            material: Material object representing the icon image.
        """
        super().__init__(name, position, size, Color(0, 0, 0, 0), layer, visible, subwidgets, subwidget_offsets, subwidget_alignments)

        self.material = material


    @property
    def material(self):
        """ Material: The material used to render the icon. """
        return self.__material
    

    @material.setter
    def material(self, value):
        if isinstance(value, Material):
            self.__material = value
            self._updated = False
        else:
            raise TypeError("Material must be a Material object:", value)


    @property
    def self_surface(self):
        surface = self.material.get_surface()
        surface = pygame.transform.scale(surface, self.size.tuple)
        return surface
    

