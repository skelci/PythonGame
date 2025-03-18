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
        text = self.__fonts[self.__font_code].render(self.text, True, self.color.tuple)

        text_rect = text.get_rect()
        self.size.x = text_rect.size[0]
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        surface.blit(text, text_rect)
        
        if self.subwidget:
            surface.blit(self.subwidget.surface, self.subwidget_pos.tuple)

        return surface
    

    @property
    def __font_code(self):
        return str(self.size.y) + self.font
    

    def __load_font(self):
        if self.__font_code not in self.__fonts:
            self.__fonts[self.__font_code] = pygame.font.Font(self.font, self.size.y)


    def draw(self, bottom_left, size):
        super().draw(bottom_left, size)


