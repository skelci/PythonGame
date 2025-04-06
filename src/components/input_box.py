#?attr CLIENT

from components.text import Text

from components.game_math import *
from components.datatypes import *



class InputBox(Text):
    def __init__(self, name, position, size, color, font, layer = 0, visible = False, max_length = 20, action = None):
        super().__init__(name, position, size, color, font, layer, visible)

        self.action = action
        self.max_length = max_length

        self.__current_text = ""
        
        self.__cursor_position = 0
        self.__is_in_focus = False
        self.__is_cursor_visible = True
        self.__cursor_blink_time = 0.5
        self.__cursor_blink_timer = 0

        self.screen_rect = (Vector(), Vector())


    @property
    def current_text(self):
        return self.__current_text
    

    @property
    def cursor_position(self):
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


    def tick(self, delta_time, pressed_keys, mouse_pos):
        if not self.visible:
            return

        if Keys.MOUSE_LEFT in pressed_keys:
            if is_in_screen_rect(*self.screen_rect, mouse_pos):
                self.__is_in_focus = True
            else:
                self.__is_in_focus = False
        
        if self.__is_in_focus:
            for key in pressed_keys:
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
                        self.__current_text = ""
                        self.__cursor_position = 0

                    case _:
                        if 32 <= key <= 126 and len(self.__current_text) < self.max_length:
                            self.__current_text = self.__current_text[:self.__cursor_position] + chr(key) + self.__current_text[self.__cursor_position:]
                            self.__cursor_position += 1

        if self.__is_cursor_visible:
            self.text = self.__current_text[:self.__cursor_position] + "|" + self.__current_text[self.__cursor_position:]
        else:
            self.text = self.__current_text[:self.__cursor_position] + " " + self.__current_text[self.__cursor_position:]

        if self.__is_in_focus:
            self.__cursor_blink_timer += delta_time
            if self.__cursor_blink_timer >= self.__cursor_blink_time:
                self.__cursor_blink_timer = 0
                self.__is_cursor_visible = not self.__is_cursor_visible
        else:
            self.__is_cursor_visible = False


