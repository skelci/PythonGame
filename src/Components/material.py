#?attr CLIENT

import pygame # type: ignore

import os



class Material:
    __textures = {}


    def __init__(self, texture_str):
        self.texture_str = texture_str
        self.load_texture()
        

    @property
    def texture_str(self):
        return self.__texture_str
    

    @texture_str.setter
    def texture_str(self, value):
        if isinstance(value, str):
            self.__texture_str = value
        else:
            raise TypeError("Texture_str must be a string or None:", value)
        

    @property
    def texture(self):
        return Material.__textures[self.texture_str]


    def load_texture(self):
        if self.texture_str not in Material.__textures:
            if os.path.isfile(self.texture_str):
                Material.__textures[self.texture_str] = pygame.image.load(self.texture_str).convert_alpha() # why the f does that shit of convert_alpha() make rendering 2x faster ?!?!?!
            else:
                raise TypeError("Texture file not found:", self.texture_str)
            


