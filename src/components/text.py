#?attr CLIENT
from components.widget import Widget

from components.datatypes import *

from engine.gl_wrapper import *

import os
import pygame



class Text(Widget):
    __fonts = {}

    def __init__(self, name, position, size, color, font, layer = 0, visible = False, text = ""):
        super().__init__(name, position, size, color, layer, visible)

        self.text = text
        self.font = font
        self.__font_size = size.y

        self.__load_font()


    @property
    def text(self):
        return self.__text
    

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self.__text = value
        else:
            raise TypeError("Text must be a string:", value)
          

    @property
    def font(self):
        return self.__font
    

    @font.setter
    def font(self, value):
        if isinstance(value, str) and os.path.exists(value):
            self.__font = value
        else:
            raise TypeError("Font must be a string:", value)
    

    @property
    def __font_code(self):
        return str(self.__font_size) + str(self.color.tuple) + self.font
    

    def __load_font(self):
        if self.__font_code not in self.__fonts:
            self.__fonts[self.__font_code] = GLWrapper.create_font_atlas(self.font, self.__font_size, self.color)


    def draw(self, bottom_left, size):
        GLWrapper.draw_text(self.text, *self.__fonts[self.__font_code], *bottom_left, size)


