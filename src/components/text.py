#?attr CLIENT
from components.widget import Widget

from components.datatypes import *

from engine.gl_wrapper import *

import os
import pygame



class Text(Widget):
    __fonts = {}

    def __init__(self, name, position, size, color, font, layer = 0, visible = False, text = "", static = True):
        super().__init__(name, position, size, color, layer, visible)

        self.text = text
        self.font = font
        self.static = static

        self.__font_size = size.y
        self.__draw_batch = QuadBatch()
        self.__updated = False

        self.__load_font()
        self.__update_size()


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
    def static(self):
        return self.__static
    

    @static.setter
    def static(self, value):
        if isinstance(value, bool):
            self.__static = value
        else:
            raise TypeError("static must be a boolean:", value)
    

    @property
    def __font_code(self):
        return str(self.__font_size) + str(self.color.tuple) + self.font
    

    def __load_font(self):
        if self.__font_code not in self.__fonts:
            self.__fonts[self.__font_code] = self.__create_font_atlas(self.font, self.__font_size, self.color)


    def __create_font_atlas(self, font_path, size, color):
        glyphs = [chr(x) for x in range(32, 127)]
        font = pygame.font.Font(font_path, size)
        
        glyph_surfaces = []
        glyph_data = {}  # char -> (x, y, w, h) in atlas
        x_offset = 0
        max_h = 0
        
        for g in glyphs:
            surf = font.render(g, True, color.tuple)
            glyph_surfaces.append((g, surf))
            if surf.get_height() > max_h:
                max_h = surf.get_height()
        
        total_w = sum(s.get_width() for _, s in glyph_surfaces)
        atlas_surf = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
        
        for g, surf in glyph_surfaces:
            atlas_surf.blit(surf, (x_offset, 0))
            glyph_data[g] = (x_offset, 0, surf.get_width(), surf.get_height())
            x_offset += surf.get_width()
        
        atlas_tex = GLWrapper.load_texture(atlas_surf)
        
        return atlas_tex, glyph_data, atlas_surf.get_size()
    

    def __update_size(self):
        width = 0
        for ch in self.text:
            if ch in self.__fonts[self.__font_code][1]:
                _, _, w, _ = self.__fonts[self.__font_code][1][ch]
                width += w

        self.size.x = width


    def __update_text(self, start_x, start_y, size_scale):
        if self.static and self.__updated:
            return
        
        text = self.text
        glyph_data, atlas_size = *self.__fonts[self.__font_code][1:], 
        
        self.__draw_batch.clear()
        x_cursor = start_x

        for ch in text:
            if ch in glyph_data:
                x, y, w, h = glyph_data[ch]

                u0, v0 = x / atlas_size[0], y / atlas_size[1]
                u1, v1 = (x + w) / atlas_size[0], (y + h) / atlas_size[1]
                
                self.__draw_batch.add_quad(x_cursor, start_y, *(Vector(w, h) * size_scale), u0, v0, u1, v1)

                x_cursor += w

        self.size.x = x_cursor - start_x
        self.__draw_batch.upload()
        self.__updated = True


    def draw(self, bottom_left, size):
        self.__update_text(*bottom_left, size)
        self.__draw_batch.draw(self.__fonts[self.__font_code][0])


    def __del__(self):
        GLWrapper.delete_texture(self.__fonts[self.__font_code][0])
        del self.__fonts[self.__font_code]


