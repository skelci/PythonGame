#?attr CLIENT

import pygame # type: ignore

import os



class Material:
    __textures = {}
    __mirrored_textures = {}


    def __init__(self, texture_str, mirrored = False):
        self.texture_str = texture_str
        self.mirrored = mirrored
        self.load_texture()
        

    @property
    def texture_str(self):
        return self.__texture_str
    

    @texture_str.setter
    def texture_str(self, value):
        if isinstance(value, str):
            self.__texture_str = value
        else:
            raise TypeError("Texture_str must be a string:", value)
        

    @property
    def mirrored(self):
        return self.__mirrored
    

    @mirrored.setter
    def mirrored(self, value):
        if isinstance(value, bool):
            self.__mirrored = value
        else:
            raise TypeError("Mirrored must be a boolean:", value)
        

    @property
    def texture(self):
        if self.mirrored:
            return Material.__mirrored_textures[self.texture_str]
        else:
            return Material.__textures[self.texture_str]


    def load_texture(self):
        if self.texture_str not in Material.__textures:
            if os.path.isfile(self.texture_str):
                Material.__textures[self.texture_str] = pygame.image.load(self.texture_str).convert_alpha() # why the f does that shit of convert_alpha() make rendering 2x faster ?!?!?!
                Material.__mirrored_textures[self.texture_str] = pygame.transform.flip(Material.__textures[self.texture_str], True, False)
            else:
                raise TypeError("Texture file not found:", self.texture_str)
            


