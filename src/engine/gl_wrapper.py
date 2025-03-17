#?attr CLIENT
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import numpy as np



class GLWrapper:
    @staticmethod
    def init():
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


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

        return tex_id


    @staticmethod
    def draw_texture(tex_id, x, y, w, h):
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glBegin(GL_QUADS)
        
        # bottom-left
        glTexCoord2f(0.0, 0.0)
        glVertex2f(x, y)
        
        # bottom-right
        glTexCoord2f(1.0, 0.0)
        glVertex2f(x + w, y)
        
        # top-right
        glTexCoord2f(1.0, 1.0)
        glVertex2f(x + w, y + h)
        
        # top-left
        glTexCoord2f(0.0, 1.0)
        glVertex2f(x, y + h)
        
        glEnd()


    @staticmethod
    def clear():
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()



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