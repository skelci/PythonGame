"""
This module contains the Material class, which is used to create a material for rendering.
"""

from engine.datatypes import *

#?ifdef CLIENT
import pygame
#?endif

import os



class Material:
    """ Represents a material for rendering. """
    
    #?ifdef CLIENT
    __textures = {}
    __scaled_textures = {}
    #?endif


    def __init__(self, texture_str: str | Color):
        """
        Args:
            texture_str: Path to the texture file or a Color object.
        """
        self.texture_str = texture_str
        #?ifdef CLIENT
        self.__load_texture()
        #?endif


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
        

    @property
    def texture(self):
        """ pygame.Surface - The original texture surface. """
        return Material.__textures[self.texture_str]


    #?ifdef CLIENT
    def __load_texture(self):
        if self.texture_str in Material.__textures:
            return
        
        if isinstance(self.texture_str, Color):
            self.__textures[self.texture_str] = pygame.Surface((1, 1), pygame.SRCALPHA if self.texture_str.a != 255 else 0)
            self.__textures[self.texture_str].fill(self.texture_str.tuple)
            self.__scaled_textures[self.texture_str] = {}
            return
        
        image = pygame.image.load(self.texture_str)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
        self.__textures[self.texture_str] = image                
        self.__scaled_textures[self.texture_str] = {}            


    def get_surface(self, size: Vector) -> pygame.Surface:
        """
        Gets the scaled pygame surface.
        Args:
            size: Width and Height of the surface to scale to.
        Returns:
            pygame.Surface - Scaled surface texture.
        """
        if size not in self.__scaled_textures[self.texture_str]:
            self.__scaled_textures[self.texture_str][size] = pygame.transform.scale(self.texture, size.tuple)

        return self.__scaled_textures[self.texture_str][size]
    
    #?endif


    def __eq__(self, value):
        if isinstance(value, Material):
            return self.texture_str == value.texture_str
        return False



