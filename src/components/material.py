from components.datatypes import Color

import pygame # type: ignore

import os



class Material:
    #?ifdef CLIENT
    __textures = {}
    __scaled_textures = {}
    #?endif


    def __init__(self, texture_str):
        self.texture_str = texture_str
        #?ifdef CLIENT
        self.__load_texture()
        #?endif


    @property
    def texture_str(self):
        return self.__texture_str
    

    @texture_str.setter
    def texture_str(self, value):
        if isinstance(value, str) or isinstance(value, Color):
            if isinstance(value, str) and not os.path.isfile(value) and not isinstance(value, Color):
                raise FileNotFoundError("Texture file not found:", value)
            self.__texture_str = value
        else:
            raise TypeError("Texture_str must be a string or Color:", value)
        

    @property
    def texture(self):
        return Material.__textures[self.texture_str]


    #?ifdef CLIENT
    def __load_texture(self):
        if self.texture_str not in Material.__textures:
            if isinstance(self.texture_str, Color):
                self.__textures[self.texture_str] = pygame.Surface((1, 1))
                self.__textures[self.texture_str].fill(self.texture_str.tuple)
                self.__scaled_textures[self.texture_str] = {}
                return
            
            if os.path.isfile(self.texture_str):
                self.__textures[self.texture_str] = pygame.image.load(self.texture_str).convert_alpha() # why the f does that shit of convert_alpha() makes rendering 2x faster ?!?!?!
                self.__scaled_textures[self.texture_str] = {}
            else:
                print("Texture file not found:", self.texture_str)


    def get_surface(self, size):
        if size not in self.__scaled_textures[self.texture_str]:
            self.__scaled_textures[self.texture_str][size] = pygame.transform.scale(self.texture, size.tuple)

        return self.__scaled_textures[self.texture_str][size]
    
    #?endif



