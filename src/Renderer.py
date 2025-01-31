from Datatypes import *
from Actor import Actor

import pygame
import math



class Renderer:
    def __init__(self, width, height, camera_width, title = "Pygame Window"):
        self.__screen = None

        self.resolution = Vector(width, height)
        self.title = title
        self.camera_width = camera_width

        self.camera_position = Vector(0, 0)

        self.__actors_to_draw = []

        self.__textures = {}


    @property
    def resolution(self):
        return self.__resolution


    @resolution.setter
    def resolution(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__resolution = value
            self.__screen = pygame.display.set_mode((value.x, value.y))
        
        else:
            raise Exception("Width must be a positive integer:", value)
        

    @property
    def title(self):
        return self.__title
    

    @title.setter
    def title(self, value):
        if isinstance(value, str):
            self.__title = value
            pygame.display.set_caption(self.__title)
        
        else:
            raise Exception("Title must be a string:", value)
        

    @property
    def camera_position(self):
        return self.__camera_position
    

    @camera_position.setter
    def camera_position(self, value):
        if isinstance(value, Vector):
            self.__camera_position = value
        
        else:
            raise Exception("Camera position must be a Vector:", value)
        

    @property
    def camera_width(self):
        return self.__camera_width
    

    @camera_width.setter
    def camera_width(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__camera_width = value
        
        else:
            raise Exception("Camera width must be a positive number:", value)
        

    @property
    def screen(self):
        return self.__screen
    

    @property
    def actors_to_draw(self):
        return self.__actors_to_draw
    

    @property
    def textures(self):
        return self.__textures


    def add_actor_to_draw(self, actor):
        if not issubclass(type(actor), Actor):
            raise Exception("Actor must be a subclass of Actor:", actor)
        
        self.__actors_to_draw.append(actor)

        if actor.texture:
            if self.textures.get(actor.texture) is None:
                self.textures[actor.texture] = pygame.image.load(actor.texture)

    
    def clear(self):
        self.__actors_to_draw = []


    def render(self):
        combined_surface = pygame.Surface((self.resolution.x, self.resolution.y))

        camera_ratio = self.resolution.y / self.camera_width
        
        for a in self.actors_to_draw:
            self.draw_rectangle_texture(combined_surface, a.texture, a.x_half_size, a.y_half_size, a.position, camera_ratio)

        self.screen.blit(combined_surface, (0, 0))
        pygame.display.flip()


    def draw_rectangle_texture(self, screen, texture_str, x_half_size, y_half_size, position, camera_ratio):
        texture = self.textures[texture_str]

        rect_width = x_half_size * 2 * camera_ratio
        rect_height = y_half_size * 2 * camera_ratio
        scaled_texture = pygame.transform.scale(texture, (rect_width, rect_height))
        
        # Calculate the top-left position to draw the texture
        top_left_position = (
            camera_ratio * (position.x - x_half_size + self.camera_position.x) + self.resolution.x / 2,
            camera_ratio * -(position.y + y_half_size + self.camera_position.y) + self.resolution.y / 2 # Invert the y-axis
        )
        
        # Draw the texture
        screen.blit(scaled_texture, top_left_position)
        
