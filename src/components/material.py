from components.datatypes import *
#?ifdef CLIENT
from engine.gl_wrapper import *
#?endif

#?ifdef CLIENT
import pygame
#?endif

import os



class Material:
    #?ifdef CLIENT
    __textures = {}
    __pygame_textures = {}
    #?endif


    def __init__(self, texture_str):
        self.texture_str = texture_str


        #?ifdef CLIENT
        if texture_str not in Material.__pygame_textures:
            if isinstance(texture_str, Color):
                tex = pygame.Surface((1, 1))
                tex.fill(texture_str.tuple)
            
            else:
                if os.path.isfile(self.texture_str):
                    tex = pygame.image.load(texture_str).convert_alpha() # why the f does that shit of convert_alpha() makes rendering 2x faster ?!?!?!
                else:
                    print("Texture file not found:", texture_str)

            Material.__pygame_textures[texture_str] = tex
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
        

    #?ifdef CLIENT
    @property
    def texture_id(self):
        if self.texture_str not in Material.__textures:
            Material.__textures[self.texture_str] = load_texture(Material.__pygame_textures[self.texture_str])
        return self.__textures[self.texture_str]
    

    @property
    def texture(self):
        return Material.__pygame_textures[self.texture_str]
    
    #?endif



