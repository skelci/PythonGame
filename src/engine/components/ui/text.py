#?attr CLIENT

"""
This module contains the Text class, which is used to create a text widget.
"""

from .widget import Widget
from engine.datatypes import *

import os
import pygame



class Text(Widget):
    """
    Represents a text widget. It renders text on the screen using a specified font and color.
    Its size is dynamically updated based on the text content and font size.
    """
    
    __fonts = {}


    def __init__(self, name: str, position: Vector, size: Vector, color: Color, font: str, layer = 0, visible = False, text = "", update_interval = 1):
        """
        Args:
            name: Name of the widget.
            position: Position of the top left corner of the widget. Vector(0, 0) is the top left corner of the screen.
            size: Size of the widget. The y value is used as font size.
            color: Color of the text.
            font: Path to the font file.
            layer: Layer of the widget. Higher layers are drawn on top of lower layers.
            visible: Whether the widget is visible or not.
            text: Text to be displayed.
        """
        super().__init__(name, position, size, color, layer, visible, update_interval = update_interval)

        self.__font_size = size.int[1]
        self.text = text
        self.font = font

        self.surface # to update the size


    @property
    def text(self):
        """ str - The text to be displayed. """
        return self.__text
    

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self.__text = value
            self.updated = False
        else:
            raise TypeError("Text must be a string:", value)
        

    @property
    def font(self):
        """ str - Path to the font file. """
        return self.__font
    

    @font.setter
    def font(self, value):
        if isinstance(value, str) and os.path.exists(value):
            self.__font = value
            self.__load_font()
            self.updated = False
        else:
            raise TypeError("Font must be a string:", value)
        

    @property
    def surface(self):
        if self.updated:
            return self._surface
        
        self._surface = Text.__fonts[self.__font_code].render(self.text, True, self.color.tuple)
        self.size.x = self._surface.get_width()
        self.updated = True

        return self._surface
    

    @property
    def __font_code(self):
        return str(self.__font_size) + self.font
    

    def __load_font(self):
        if self.__font_code not in self.__fonts:
            self.__fonts[self.__font_code] = pygame.font.Font(self.font, self.__font_size)


