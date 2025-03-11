from componentst.widget import Widget
from componentst.datatypes import *

import pygame



class Border(Widget):
    def __init__(self, name, position, size, layer, border_color, bg_color = Color(0, 0, 0, 0), visible = False, thickness = 10):
        super().__init__(name, position, size, layer, bg_color, visible)

        self.border_color = border_color
        self.thickness = thickness


    @property
    def border_color(self):
        return self.__border_color
    

    @border_color.setter
    def border_color(self, value):
        if isinstance(value, Color):
            self.__border_color = value
        else:
            raise TypeError("Border color must be a Color:", value)


    @property
    def thickness(self):
        return self.__thickness
    

    @thickness.setter
    def thickness(self, value):
        if isinstance(value, int) and 0 <= value <= min(*self.size):
            self.__thickness = value
        else:
            raise TypeError("Thickness must be an integer between 0 and the half of the smallest dimension of the widget:", value)
        

    @property
    def surface(self):
        surface = super().surface
        rect = pygame.Rect((0, 0), self.size.tuple)
        pygame.draw.rect(surface, self.border_color.tuple, rect, self.thickness)

        return surface
    
