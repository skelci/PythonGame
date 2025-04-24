#?attr CLIENT

"""
This module contains the InputBox class, which is used to create an input box widget.
"""

from components.text import Text

from components.game_math import *
from components.datatypes import *

from typing import Callable



class InputBox(Text):
    """
    Represents an input box widget. It allows the user to enter text and provides a cursor for text editing.
    The input box can be focused and unfocused, and it supports basic text editing operations such as backspace, delete, and cursor movement.
    The input box can also trigger an action when the user presses the enter key.
    """


    def __init__(self, name: str, position: Vector, size: Vector, color: Color, font: str, layer = 0, visible = False, max_length = 20, action: Callable[[str], None] = None):
        """
        Refer to the Text class for more information about the parameters.
        Args:
            max_length: Maximum length of the text that can be entered. Default is 20.
            action: Function to be called when the user presses the enter key. Default is None.
        """
        self.__original_size = size.copy
        super().__init__(name, position, size, color, font, layer, visible)

        self.action = action
        self.max_length = max_length

        self.__current_text = ""
        
        self.__cursor_position = 0
        self.__is_in_focus = False
        self.__is_cursor_visible = True
        self.__cursor_blink_time = 0.5
        self.__cursor_blink_timer = self.__cursor_blink_time

        self.screen_rect = (Vector(), 0)


    @property
    def current_text(self):
        """ str - The current text in the input box. """
        return self.__current_text
    

    @property
    def is_cursor_visible(self):
        """ bool - Whether the cursor is currently visible. """
        return self.__is_cursor_visible
    

    @property
    def is_in_focus(self):
        """ bool - Whether the input box is currently in focus. """
        return self.__is_in_focus
    

    @is_in_focus.setter
    def is_in_focus(self, value: bool):
        if isinstance(value, bool):
            self.__is_in_focus = value
            if value:
                self.__cursor_position = len(self.__current_text)
                self.__is_cursor_visible = True
        else:
            raise TypeError("Is in focus must be a boolean:", value)
    

    @property
    def cursor_position(self):
        """ int - The current position of the cursor in the text. """
        return self.__cursor_position
    

    @current_text.setter
    def current_text(self, value):
        if isinstance(value, str):
            self.__current_text = value[:self.max_length]
            self.__cursor_position = len(self.__current_text)
        else:
            raise TypeError("Current text must be a string:", value)
        

    @property
    def action(self):
        """ Callable[[str], None] - The action to be called when the user presses the enter key. """
        return self.__action
    

    @action.setter
    def action(self, value):
        if value is None or callable(value):
            self.__action = value
        else:
            raise TypeError("Action must be a function:", value)


    @property
    def screen_rect(self):
        """ tuple[Vector, Vector] - The screen rectangle of the input box. The first element is the top left corner, second elemnent is bottom right corner. """
        return self.__screen_rect
    

    @screen_rect.setter
    def screen_rect(self, value):
        if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], Vector) and isinstance(value[1], (int, float)):
            top_left = value[0]
            self.__screen_rect = (top_left, top_left + self.__original_size * value[1])
        else:
            raise TypeError("Screen rect must be a tuple of Vector and float:", value)


    def tick(self, delta_time: float, triggered_keys: set[Keys], pressed_keys: set[Keys], mouse_pos: Vector):
        """
        Updates the input box state based on the triggered keys, pressed keys, and mouse position.
        Args:
            delta_time: Time since the last frame in seconds.
            triggered_keys: Set of keys that were pressed in this frame.
            pressed_keys: Set of keys that are currently pressed.
            mouse_pos: Position of the mouse cursor.
        """
        if not self.visible:
            return

        if Keys.MOUSE_LEFT in triggered_keys:
            self.is_in_focus = is_in_screen_rect(*self.screen_rect, mouse_pos)
        
        if self.is_in_focus:
            for key in triggered_keys:
                match key:
                    case Keys.BACKSPACE:
                        if self.__cursor_position > 0:
                            self.__current_text = self.__current_text[:self.__cursor_position - 1] + self.__current_text[self.__cursor_position:]
                            self.__cursor_position -= 1
                    
                    case Keys.DELETE:
                        if self.__cursor_position < len(self.__current_text):
                            self.__current_text = self.__current_text[:self.__cursor_position] + self.__current_text[self.__cursor_position + 1:]

                    case Keys.LEFT:
                        if self.__cursor_position > 0:
                            self.__cursor_position -= 1

                    case Keys.RIGHT:
                        if self.__cursor_position < len(self.__current_text):
                            self.__cursor_position += 1

                    case Keys.HOME:
                        self.__cursor_position = 0

                    case Keys.END:
                        self.__cursor_position = len(self.__current_text)

                    case Keys.ENTER:
                        self.__is_in_focus = False
                        self.__is_cursor_visible = False
                        self.action(self.__current_text) if self.action else None

                    case _:
                        if 32 <= key <= 126 and len(self.__current_text) < self.max_length:
                            base_char = chr(key)
                            if Keys.LEFT_SHIFT in pressed_keys or Keys.RIGHT_SHIFT in pressed_keys:
                                shifted_map = { # Slovenian keyboard layout
                                    '1': '!', '2': '"', '3': '#', '4': '$', '5': '%',
                                    '6': '&', '7': '/', '8': '(', '9': ')', '0': '=',
                                    '\'': '?', '+': '*', ',': ';', '.': ':', '-': '_',
                                    '<': '>'
                                }
                                char = shifted_map.get(base_char, base_char.upper())
                            else:
                                char = base_char

                            self.__current_text = self.__current_text[:self.cursor_position] + char + self.current_text[self.cursor_position:]
                            self.__cursor_position += 1

        if self.is_cursor_visible:
            self.text = self.current_text[:self.cursor_position] + "|" + self.current_text[self.cursor_position:]
        else:
            self.text = self.current_text[:self.cursor_position] + " " + self.current_text[self.cursor_position:]

        if self.is_in_focus:
            self.__cursor_blink_timer += delta_time
            if self.__cursor_blink_timer >= self.__cursor_blink_time:
                self.__cursor_blink_timer = 0
                self.__is_cursor_visible = not self.is_cursor_visible
        else:
            self.__is_cursor_visible = False
            self.__cursor_blink_timer = 0


