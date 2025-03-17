#?attr CLIENT

from components.datatypes import *
from components.actor import Actor
from components.widget import Widget
from components.button import Button

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
import numpy as np

import time



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



class Renderer:
    def __init__(self, resolution, camera_width, title = "Pygame Window", fullscreen = False, windowed = True, camera_position = Vector()):
        self.__screen = None
        self.__fullscreen = False
        self.__windowed = True

        self.resolution = resolution
        self.title = title
        self.camera_width = camera_width
        self.fullscreen = fullscreen
        self.windowed = windowed
        self.camera_position = camera_position

        self.__actors_to_draw = []
        self.__widgets_to_draw = []

        GLWrapper().init()


    @property
    def resolution(self):
        return self.__resolution


    @resolution.setter
    def resolution(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__resolution = value
            self.__screen = pygame.display.set_mode((value.x, value.y),
                                                    FULLSCREEN if self.fullscreen else 0 |
                                                    NOFRAME if not self.windowed else 0 |
                                                    DOUBLEBUF | HWSURFACE | OPENGL)
            GLWrapper().update_resolution(value)
        else:
            raise TypeError("Width must be a positive integer:", value)
        

    @property
    def title(self):
        return self.__title
    

    @title.setter
    def title(self, value):
        if isinstance(value, str):
            self.__title = value
            pygame.display.set_caption(self.__title)
        else:
            raise TypeError("Title must be a string:", value)
        

    @property
    def camera_position(self):
        return self.__camera_position
    

    @camera_position.setter
    def camera_position(self, value):
        if isinstance(value, Vector):
            self.__camera_position = value
        else:
            raise TypeError("Camera position must be a Vector:", value)
        

    @property
    def camera_width(self):
        return self.__camera_width
    

    @camera_width.setter
    def camera_width(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__camera_width = value
        else:
            raise TypeError("Camera width must be a positive number:", value)
        

    @property
    def fullscreen(self):
        return self.__fullscreen
    

    @fullscreen.setter
    def fullscreen(self, value):
        if isinstance(value, bool):
            self.__fullscreen = value
            self.__screen = pygame.display.set_mode((self.resolution.x, self.resolution.y),
                                                    FULLSCREEN if value else 0 |
                                                    NOFRAME if not self.windowed else 0 |
                                                    DOUBLEBUF | HWSURFACE | OPENGL)
        else:
            raise TypeError("Fullscreen must be a bool:", value)
        

    @property
    def windowed(self):
        return self.__windowed
    

    @windowed.setter
    def windowed(self, value):
        if isinstance(value, bool):
            self.__windowed = value
            self.__screen = pygame.display.set_mode((self.resolution.x, self.resolution.y),
                                                    FULLSCREEN if self.fullscreen else 0 |
                                                    NOFRAME if not value else 0 |
                                                    DOUBLEBUF | HWSURFACE | OPENGL)
        else:
            raise TypeError("Windowed must be a bool:", value)
        

    @property
    def screen(self):
        return self.__screen
    

    @property
    def actors_to_draw(self):
        return self.__actors_to_draw
    

    @property
    def widgets_to_draw(self):
        return self.__widgets_to_draw


    def add_actor_to_draw(self, actor):
        if not isinstance(actor, Actor):
            raise TypeError("Actor must be a subclass of Actor:", actor)
        
        self.__actors_to_draw.append(actor)


    def add_widget_to_draw(self, widget):
        if not isinstance(widget, Widget):
            raise TypeError("Widget must be a subclass of Widget:", widget)
        
        self.__widgets_to_draw.append(widget)

    
    def __clear(self):
        self.__actors_to_draw.clear()
        self.__widgets_to_draw.clear()
        GLWrapper.clear()


    def render(self):
        camera_ratio = self.resolution.x / self.camera_width
        
        time_start = time.time()

        quad_batches = {}

        for a in self.actors_to_draw:
            bottom_left_position = (a.position - a.half_size - self.camera_position) * camera_ratio + self.resolution / 2
            size = a.half_size * 2 * camera_ratio

            tex_id = a.material.texture_id
            if tex_id not in quad_batches:
                quad_batches[tex_id] = QuadBatch()

            quad_batches[tex_id].add_quad(*bottom_left_position, *size)

        for tex_id, batch in quad_batches.items():
            batch.upload()
            batch.draw_batch(tex_id)

        time_actors = time.time()

        self.__widgets_to_draw.sort(key = lambda w: w.layer)
        for w in self.widgets_to_draw:
            self.__draw_widget(w)

        time_widgets = time.time()

        pygame.display.flip()

        self.__clear()

        return (time_actors - time_start, time_widgets - time_actors)


    def draw_background(self, background):
        pass
        # if background is None:
        #     self.screen.fill((0, 0, 0))
        #     return
        
        # bg_surface = background.get_bg_surface(self.camera_position, self.resolution, self.camera_width)
        # self.screen.blit(bg_surface, (0, 0))


    def __draw_widget(self, widget):
        camera_ratio = self.resolution / Vector(1600, 900)

        top_left_position = camera_ratio * widget.position

        size = widget.size * camera_ratio.x

        widget.screen_rect = (top_left_position, top_left_position + size)

        surface = pygame.transform.scale(widget.surface, size.tuple)

        # self.screen.blit(surface, top_left_position)
        
