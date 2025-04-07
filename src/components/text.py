#?attr CLIENT

from components.widget import Widget

import os
import pygame



class Text(Widget):
    __fonts = {}

    def __init__(self, name, position, size, color, font, layer = 0, visible = False, text = ""):
        super().__init__(name, position, size, color, layer, visible)

        self.__font_size = size.y
        self.text = text
        self.font = font

        self.surface # to update the size


    @property
    def text(self):
        return self.__text
    

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self.__text = value
            self._updated = False
        else:
            raise TypeError("Text must be a string:", value)
        

    @property
    def font(self):
        return self.__font
    

    @font.setter
    def font(self, value):
        if isinstance(value, str) and os.path.exists(value):
            self.__font = value
            self.__load_font()
            self._updated = False
        else:
            raise TypeError("Font must be a string:", value)
        

    @property
    def surface(self):
        if self._updated:
            return self.__surface
        
        self.__surface = self.__fonts[self.__font_code].render(self.text, True, self.color.tuple)
        self.size.x = self.__surface.get_width()
        self._updated = True

        return self.__surface
    

    @property
    def __font_code(self):
        return str(self.__font_size) + self.font
    

    def __load_font(self):
        if self.__font_code not in self.__fonts:
            self.__fonts[self.__font_code] = pygame.font.Font(self.font, self.__font_size)


