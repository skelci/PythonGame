"""
This module contains the Material class, which is used to create a material for rendering.
"""

from engine.datatypes import *

#?ifdef CLIENT
import pygame
from OpenGL.GL import *
#?endif

import os



class Material:
    """ Represents a material for rendering. """
    
    #?ifdef CLIENT
    __textures = {}
    #?endif


    def __init__(self, texture_str: str | Color):
        """
        Args:
            texture_str: Path to the texture file or a Color object.
        """
        self.texture_str = texture_str


    @property
    def texture_str(self):
        """ str | Color - Path to the texture file or a Color object. """
        return self.__texture_str
    

    @texture_str.setter
    def texture_str(self, value):
        if isinstance(value, str) or isinstance(value, Color):
            #?ifdef CLIENT
            if isinstance(value, str) and not os.path.isfile(value) and not isinstance(value, Color):
                raise FileNotFoundError("Texture file not found:", value)
            #?endif
            self.__texture_str = value
        else:
            raise TypeError("Texture_str must be a string or Color:", value)
        

    #?ifdef CLIENT
    @property
    def texture(self):
        """ OpenGL texture ID. """
        return Material.__textures[self.texture_str]


    @property
    def size(self):
        """ Vector - Size of the texture in pixels. """
        return self.__size


    def load(self):
        """ Called only by the engine. """
        if self.texture_str in Material.__textures:
            return
        
        if isinstance(self.texture_str, Color):
            image = pygame.Surface((1, 1), pygame.SRCALPHA if self.texture_str.a != 255 else 0)
            image.fill(self.texture_str.tuple)
            self.__textures[self.texture_str] = image

        else:     
            image = pygame.image.load(self.texture_str)
            if image.get_alpha() is None:
                image = image.convert()
            else:
                image = image.convert_alpha()

        self.__textures[self.texture_str] = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.__textures[self.texture_str])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        width, height = image.get_size()
        self.__size = Vector(width, height)
        image_data = pygame.image.tostring(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    
    def use(self):
        """ Called only by the renderer. """
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
    #?endif


    def __eq__(self, value):
        if isinstance(value, Material):
            return self.texture_str == value.texture_str
        return False



