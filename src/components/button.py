#?attr CLIENT
from components.border import Border

from components.text import Text
from components.datatypes import *
from components.game_math import *



class Button(Border):
    def __init__(self, name, position, size, layer, border_color, bg_color = Color(0, 0, 0, 0), visible = False, thickness = 10, subwidgets = {}, subwidget_offsets = {}, subwidget_alignments = {}, hover_color = Color(0, 0, 0), click_color = Color(0, 0, 0), action = None):
        self.__main_color = bg_color
        super().__init__(name, position, size, layer, border_color, bg_color, visible, thickness, subwidgets, subwidget_offsets, subwidget_alignments)

        self.hover_color = hover_color
        self.click_color = click_color
        self.action = action

        self.screen_rect = (Vector(), 0)


    @property
    def hover_color(self):
        return self.__hover_color
    

    @hover_color.setter
    def hover_color(self, value):
        if isinstance(value, Color):
            self.__hover_color = value
        else:
            raise TypeError("Hover color must be a Color:", value)
        

    @property
    def click_color(self):
        return self.__click_color
    

    @click_color.setter
    def click_color(self, value):
        if isinstance(value, Color):
            self.__click_color = value
        else:
            raise TypeError("Click color must be a Color:", value)
        

    @property
    def action(self):
        return self.__action
    

    @action.setter
    def action(self, value):
        if value is None or callable(value):
            self.__action = value
        else:
            raise TypeError("Action must be a function:", value)
        

    @property
    def screen_rect(self):
        return self.__screen_rect
    

    @screen_rect.setter
    def screen_rect(self, value):
        if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], Vector) and isinstance(value[1], (int, float)):
            top_left = value[0]
            self.__screen_rect = (top_left, top_left + self.size * value[1])
        else:
            raise TypeError("Screen rect must be a tuple of Vector and float:", value)
        

    @property
    def main_color(self):
        return self.__main_color
    

    def tick(self, pressed_keys, left_click, mouse_pos):
        if not self.visible:
            return

        if is_in_screen_rect(*self.screen_rect, mouse_pos):
            if Keys.MOUSE_LEFT in pressed_keys:
                self.color = self.click_color
            else:
                self.color = self.hover_color

            if left_click and self.action is not None:
                self.action()

        else:
            self.color = self.main_color

        
        
