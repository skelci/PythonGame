#?attr CLIENT
from components.widget import Widget
from components.datatypes import *

import pygame



class Border(Widget):
    def __init__(self, name, position, size, color, layer = 0, visible = False, subwidget = None, subwidget_offset = Vector(), subwidget_alignment = Alignment.CENTER, thickness = 10):
        super().__init__(name, position, size, color, layer, visible, subwidget, subwidget_offset, subwidget_alignment)

        self.thickness = thickness


    @property
    def thickness(self):
        return self.__thickness


    @thickness.setter
    def thickness(self, value):
        if isinstance(value, (int, float)) and 0 <= value <= min(self.size):
            self.__thickness = value
        else:
            raise TypeError("Thickness must be a float between 0 and the half of the smallest dimension of the widget:", value)
        

    @property
    def surface(self):
        surface = pygame.Surface(self.size.tuple, pygame.SRCALPHA)
        rect = pygame.Rect((0, 0), self.size.tuple)
        pygame.draw.rect(surface, self.color.tuple, rect, self.thickness)

        if self.subwidget:
            surface.blit(self.subwidget.surface, self.subwidget_pos.tuple)

        return surface
    

    def draw(self, bottom_left, size):
        super().draw(bottom_left, size)
    
