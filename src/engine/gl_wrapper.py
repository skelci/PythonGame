#?attr CLIENT
from components.datatypes import *

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import numpy as np



class QuadBatch:
    def __init__(self):
        self.vbo_id = glGenBuffers(1)
        self.vertex_data = []
        self.count_quads = 0


    def add_quad(self, x, y, w, h, u0=0.0, v0=0.0, u1=1.0, v1=1.0):
        # bottom-left
        self.vertex_data.extend([x,      y,      u0, v0])
        # bottom-right
        self.vertex_data.extend([x + w,  y,      u1, v0])
        # top-right
        self.vertex_data.extend([x + w,  y + h,  u1, v1])
        # top-left
        self.vertex_data.extend([x,      y + h,  u0, v1])

        self.count_quads += 1


    def upload(self):
        # Convert list to numpy float32 array
        arr = np.array(self.vertex_data, dtype=np.float32)

        # Bind and upload data to our VBO
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id)
        glBufferData(GL_ARRAY_BUFFER, arr.nbytes, arr, GL_STATIC_DRAW)


    def draw_batch(self, texture_id):
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id)

        # Enable vertex + texcoord pointers
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        # Interleave: 2 floats for position, then 2 for UVs => stride is 4 * sizeof(float)
        glVertexPointer(2, GL_FLOAT, 16, ctypes.c_void_p(0))
        glTexCoordPointer(2, GL_FLOAT, 16, ctypes.c_void_p(8))  # offset by 2 floats

        # Each quad has 4 vertices, so total vertices = count_quads * 4
        glDrawArrays(GL_QUADS, 0, self.count_quads * 4)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, 0)


    def clear(self):
        self.vertex_data.clear()
        self.count_quads = 0



class GLWrapper:
    draw_batch = None

    @staticmethod
    def init():
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        GLWrapper.draw_batch = QuadBatch()


    @staticmethod
    def update_resolution(resolution):
        width, height = resolution
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    @staticmethod
    def load_texture(surface):
        texture_data = pygame.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return tex_id
    

    @staticmethod
    def delete_texture(tex_id):
        glDeleteTextures(int(tex_id))
    

    @staticmethod
    def draw_quad(x, y, w, h):
        glBegin(GL_QUADS)

        glTexCoord2f(0.0, 0.0)
        glVertex2f(x, y)

        glTexCoord2f(1.0, 0.0)
        glVertex2f(x + w, y)

        glTexCoord2f(1.0, 1.0)
        glVertex2f(x + w, y + h)

        glTexCoord2f(0.0, 1.0)
        glVertex2f(x, y + h)

        glEnd()


    @staticmethod
    def draw_texture(tex_id, x, y, w, h):
        glBindTexture(GL_TEXTURE_2D, tex_id)
        GLWrapper.draw_quad(x, y, w, h)


    @staticmethod
    def draw_colored_quad(x, y, w, h, color):
        glColor4f(*color.normalized)
        GLWrapper.draw_quad(x, y, w, h)


    @staticmethod
    def create_font_atlas(font_path, size, color):
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


    @staticmethod
    def draw_text(text, atlas_tex, glyph_data, atlas_size, start_x, start_y, size_scale):
        x_cursor = start_x

        for ch in text:
            if ch in glyph_data:
                x, y, w, h = glyph_data[ch]

                u0, v0 = x / atlas_size[0], y / atlas_size[1]
                u1, v1 = (x + w) / atlas_size[0], (y + h) / atlas_size[1]
                
                GLWrapper.draw_batch.add_quad(x_cursor, start_y, *(Vector(w, h) * size_scale), u0, v0, u1, v1)

                x_cursor += w

        GLWrapper.draw_batch.upload()
        GLWrapper.draw_batch.draw_batch(atlas_tex)
        GLWrapper.draw_batch.clear()


    @staticmethod
    def clear():
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()


