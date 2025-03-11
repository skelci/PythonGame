from componentst.border import Border

from componentst.text import Text
from componentst.datatypes import *
from componentst.game_math import *



class Button(Border):
    def __init__(self, name, position, size, layer, border_color, bg_color, font, visible = False, thickness = 10, text = "", text_color = Color(0, 0, 0), font_size = 32, text_alignment = Alignment.CENTER, hover_color = Color(0, 0, 0), click_color = Color(0, 0, 0), action = None):
        self.__main_color = bg_color
        super().__init__(name, position, size, layer, border_color, bg_color, visible, thickness)

        self.__text = Text(name + "_text", position, size, layer, font, Color(0, 0, 0, 0), visible, text, text_color, font_size, text_alignment)

        self.hover_color = hover_color
        self.click_color = click_color
        self.action = action

        self.screen_rect = (Vector(), Vector())


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
        if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], Vector) and isinstance(value[1], Vector):
            self.__screen_rect = value
        else:
            raise TypeError("Screen rect must be a tuple of two Vectors:", value)
        

    @property
    def main_color(self):
        return self.__main_color


    @property
    def surface(self):
        surface = super().surface
        surface.blit(self.__text.surface, (0, 0))
        return surface
    

    def tick(self, pressed_keys, left_click, mouse_pos):
        if not self.visible:
            return

        if is_in_screen_rect(*self.screen_rect, mouse_pos):
            if Key.MOUSE_LEFT in pressed_keys:
                self.color = self.click_color
            else:
                self.color = self.hover_color

            if left_click and self.action is not None:
                self.action()

        else:
            self.color = self.main_color

        
        
