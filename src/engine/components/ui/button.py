#?attr CLIENT

"""
This module contains the Button class, which is used to create a button widget.
"""

from .border import Border

from engine.datatypes import *
from engine.game_math import *
from .widget import Widget

from typing import Callable



class Button(Border):
    """
    Represents a button widget. It inherists from the Border class and adds functionality for hover and click effects.
    The button can trigger an action when clicked, and it can change its color based on hover and click states.
    """

    def __init__(self, name: str, position: Vector, size: Vector, layer = 0, border_color: Color = Color(255, 255, 255), bg_color: Color = Color(0, 0, 0, 0), visible = False, thickness = 10, subwidgets: dict[str, Widget] = {}, subwidget_offsets: dict[str, Vector] = {}, subwidget_alignments: dict[str, Alignment] = {}, hover_color: Color = Color(0, 0, 0), click_color: Color = Color(0, 0, 0), action: Callable[[], None] = None, update_interval = 1):
        """
        Refer to the Border class for more information about the parameters.
        Args:
            hover_color: Color of the button when hovered over. Default is Color(0, 0, 0).
            click_color: Color of the button when clicked. Default is Color(0, 0, 0).
            action: Function to be called when the button is clicked. Default is None.
        """
        self.__main_color = bg_color
        super().__init__(name, position, size, layer, border_color, bg_color, visible, thickness, subwidgets, subwidget_offsets, subwidget_alignments, update_interval)

        self.hover_color = hover_color
        self.click_color = click_color
        self.action = action

        self.screen_rect = (Vector(), 0)


    @property
    def hover_color(self):
        """ Color - Color of the button when hovered over. """
        return self.__hover_color
    

    @hover_color.setter
    def hover_color(self, value):
        if isinstance(value, Color):
            self.__hover_color = value
        else:
            raise TypeError("Hover color must be a Color:", value)
        

    @property
    def click_color(self):
        """ Color - Color of the button when clicked. """
        return self.__click_color
    

    @click_color.setter
    def click_color(self, value):
        if isinstance(value, Color):
            self.__click_color = value
        else:
            raise TypeError("Click color must be a Color:", value)
        

    @property
    def action(self):
        """ Callable[[], None] - The action to be called when the button is clicked. """
        return self.__action
    

    @action.setter
    def action(self, value):
        if value is None or callable(value):
            self.__action = value
        else:
            raise TypeError("Action must be a function:", value)
        

    @property
    def screen_rect(self):
        """ tuple[Vector, Vector] - The screen rectangle of the button. The first element is the top left corner and the second element is the bottom right corner. """
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
        """ Color - The main color of the button. """
        return self.__main_color
    

    def tick(self, pressed_keys: set[Keys], left_click: bool, mouse_pos: Vector):
        """
        Updates the button state based on the pressed keys and mouse position.
        Args:
            pressed_keys: Set of keys that are currently pressed.
            left_click: Whether the left mouse button is clicked or not.
            mouse_pos: Position of the mouse cursor.
        """
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



