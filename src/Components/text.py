from components.widget import Widget

from components.datatypes import *

import os
import pygame



class Text(Widget):
    __fonts = {}

    def __init__(self, name, position, size, layer, font, bg_color = Color(0, 0, 0, 0), visible = False, text = "", text_color = Color(255, 255, 255), font_size = 32, text_alignment = Alignment.CENTER):
        super().__init__(name, position, size, layer, bg_color, visible)

        self.text = text
        self.text_color = text_color
        self.font = font
        self.font_size = font_size
        self.text_alignment = text_alignment


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
    def text_color(self):
        return self.__text_color
    

    @text_color.setter
    def text_color(self, value):
        if isinstance(value, Color):
            self.__text_color = value
        else:
            raise TypeError("Text color must be a Color:", value)
        

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
    def font_size(self):
        return self.__font_size
    

    @font_size.setter
    def font_size(self, value):
        if isinstance(value, int) and value > 0:
            self.__font_size = value
            self.load_font()
        else:
            raise TypeError("Font size must be a positive integer:", value)
        

    @property
    def text_alignment(self):
        return self.__text_alignment
    

    @text_alignment.setter
    def text_alignment(self, value):
        if isinstance(value, Alignment):
            self.__text_alignment = value
        else:
            raise TypeError("Text alignment must be an Alignment:", value)
        

    @property
    def surface(self):
        text = self.__fonts[self.__font_code].render(self.text, True, self.text_color.tuple)
        text_rect = None
        match self.text_alignment:
            case Alignment.LEFT:
                text_rect = text.get_rect(topleft = (0, 0))
            case Alignment.CENTER:
                text_rect = text.get_rect(center = (self.size / 2).rounded.tuple)
            case Alignment.RIGHT:
                text_rect = text.get_rect(topright = (self.size.x, 0))

        surface = super().surface
        surface.blit(text, text_rect)

        return surface
    

    @property
    def __font_code(self):
        return str(self.font_size) + self.font
    

    def load_font(self):
        if self.__font_code not in self.__fonts:
            self.__fonts[self.__font_code] = pygame.font.Font(self.font, self.font_size)


