#?attr CLIENT

from components.datatypes import *
from components.actor import Actor
from components.widget import Widget
from components.button import Button

from engine.gl_wrapper import *

import pygame
from pygame.locals import *

import time



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
        if background is None:
            return
        
        background.draw_bg_surface(self.camera_position, self.resolution, self.camera_width)


    def __draw_widget(self, widget):
        camera_ratio = self.resolution / Vector(1600, 900)

        top_left_position = camera_ratio * widget.position

        size = widget.size * camera_ratio.x

        widget.screen_rect = (top_left_position, top_left_position + size)

        # surface = pygame.transform.scale(widget.surface, size.tuple)

        # self.screen.blit(surface, top_left_position)
        
