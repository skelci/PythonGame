#?attr CLIENT

from components.datatypes import *
from components.actor import Actor
from components.widget import Widget
from components.button import Button

import pygame # type: ignore

import time



class Renderer:
    def __init__(self, width, height, camera_width, title = "Pygame Window", fullscreen = False, windowed = True, camera_position = Vector()):
        self.__screen = None
        self.__fullscreen = False
        self.__windowed = True

        self.resolution = Vector(width, height)
        self.title = title
        self.camera_width = camera_width
        self.fullscreen = fullscreen
        self.windowed = windowed
        self.camera_position = camera_position

        self.__actors_to_draw = []
        self.__widgets_to_draw = []


    @property
    def resolution(self):
        return self.__resolution


    @resolution.setter
    def resolution(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__resolution = value
            self.__screen = pygame.display.set_mode((value.x, value.y),
                                                    pygame.FULLSCREEN if self.fullscreen else 0 |
                                                    pygame.NOFRAME if not self.windowed else 0 |
                                                    pygame.DOUBLEBUF | pygame.HWSURFACE)
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
                                                    pygame.FULLSCREEN if value else 0 |
                                                    pygame.NOFRAME if not self.windowed else 0 |
                                                    pygame.DOUBLEBUF | pygame.HWSURFACE)
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
                                                    pygame.FULLSCREEN if self.fullscreen else 0 |
                                                    pygame.NOFRAME if not value else 0 |
                                                    pygame.DOUBLEBUF | pygame.HWSURFACE)
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

    
    def clear(self):
        self.__actors_to_draw.clear()
        self.__widgets_to_draw.clear()


    def render(self):
        camera_ratio = self.resolution.x / self.camera_width
        
        time_start = time.time()

        for a in self.actors_to_draw:
            top_left_position = (
                camera_ratio * (a.position.x - a.half_size.x - self.camera_position.x) + self.resolution.x / 2,
                camera_ratio * -(a.position.y + a.half_size.y - self.camera_position.y) + self.resolution.y / 2 # Invert the y-axis
            )

            surface = a.material.get_surface(a.half_size * camera_ratio * 2 * 1.02) # 1.02 is a magic number to prevent gaps between the textures
            self.screen.blit(surface, top_left_position)

        time_actors = time.time()

        self.__widgets_to_draw.sort(key = lambda w: w.layer)
        for w in self.widgets_to_draw:
            self.__draw_widget(w)

        time_widgets = time.time()

        pygame.display.flip()

        return (time_actors - time_start, time_widgets - time_actors)


    def draw_background(self, background):
        bg_surface = background.get_bg_surface(self.camera_position, self.resolution, self.camera_width)
        self.screen.blit(bg_surface, (0, 0))


    def __draw_widget(self, widget):
        camera_ratio = self.resolution / Vector(1600, 900)
        top_left_position = camera_ratio * widget.position

        size = widget.size * camera_ratio.x

        widget.screen_rect = (top_left_position, top_left_position + size)

        surface = widget.surface
        surface = pygame.transform.scale(surface, size.tuple)

        self.screen.blit(surface, top_left_position.tuple)



