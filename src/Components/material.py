import pygame
import os



class Material:
    __textures = {}
    __mirrored_textures = {}


    def __init__(self, name, texture_str, mirrored = False):
        self.name = name
        self.texture_str = texture_str
        self.mirrored = mirrored
        self.load_texture()


    @property
    def name(self):
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise Exception("Name must be a string:", value)
        

    @property
    def texture_str(self):
        return self.__texture_str
    

    @texture_str.setter
    def texture_str(self, value):
        if isinstance(value, str):
            self.__texture_str = value
        else:
            raise Exception("Texture_str must be a string:", value)
        

    @property
    def mirrored(self):
        return self.__mirrored
    

    @mirrored.setter
    def mirrored(self, value):
        if isinstance(value, bool):
            self.__mirrored = value
        else:
            raise Exception("Mirrored must be a boolean:", value)
        

    @property
    def texture(self):
        if self.mirrored:
            return Material.__mirrored_textures[self.texture_str]
        else:
            return Material.__textures[self.texture_str]


    def load_texture(self):
        if self.texture_str not in Material.__textures:
            if os.path.isfile(self.texture_str):
                Material.__textures[self.texture_str] = pygame.image.load(self.texture_str)
                Material.__mirrored_textures[self.texture_str] = pygame.transform.flip(Material.__textures[self.texture_str], True, False)
            else:
                raise Exception("Texture file not found:", self.texture_str)
    
