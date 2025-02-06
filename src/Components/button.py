from components.border import Border

from components.datatypes import *



class Button(Border):
    def __init__(self, name, position, size, layer, border_color, bg_color, visible = False, thickness = 10, text = "", text_color = Color(0, 0, 0), font = "Arial", font_size = 32):
        super().__init__(name, position, size, layer, border_color, bg_color, visible, thickness)
