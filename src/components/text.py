from components.widget import Widget

from components.datatypes import *

from engine.gl_wrapper import *

import os
import pygame



class Text(Widget):
    __fonts = {}

    def __init__(self, name, position, size, color, font, layer = 0, visible = False, subwidget = None, subwidget_offset = Vector(), subwidget_alignment = Alignment.CENTER, text = ""):
        super().__init__(name, position, size, color, layer, visible, subwidget, subwidget_offset, subwidget_alignment)

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
    def surface(self):
        text = self.__fonts[self.__font_code].render(self.text, True, self.color.tuple)

        text_rect = text.get_rect(topleft = (0, 0))
        self.size = Vector(*text_rect.size)
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.blit(text, text_rect)
        
        if self.subwidget:
            surface.blit(self.subwidget.surface, self.subwidget_pos.tuple)

        return surface
    

    @property
    def __font_code(self):
        return str(self.__font_size) + self.font
    

    def __load_font(self):
        if self.__font_code not in self.__fonts:
            self.__fonts[self.__font_code] = pygame.font.Font(self.font, self.__font_size)


    def draw(self, bottom_left, size):
        super().draw(bottom_left, size)


