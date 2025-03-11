from components.datatypes import *

import pygame



class BackgroundLayer:
    def __init__(self, material, width, scroll_speed):
        self.material = material
        self.width = width
        self.scroll_speed = scroll_speed

        self.__buffered_screen_res = None
        self.__buffered_camera_width = None


    @property
    def material(self):
        return self.__material
    

    @material.setter
    def material(self, value):
        if value.__class__.__name__ == "Material":
            self.__material = value
            self.__texture = value.texture
        else:
            raise TypeError("Texture must be a Material instance.")
        

    @property
    def width(self):
        return self.__width
    

    @width.setter
    def width(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__width = value
        else:
            raise TypeError("Width must be a positive number.")
        

    @property
    def scroll_speed(self):
        return self.__scroll_speed
    

    @scroll_speed.setter
    def scroll_speed(self, value):
        if isinstance(value, (int, float)):
            self.__scroll_speed = value
        else:
            raise TypeError("Scroll speed must be a number.")
        

    def __set_buffer(self, screen_res, camera_width):
        self.__buffered_screen_res = screen_res
        self.__buffered_camera_width = camera_width
        

    def __create_bg_surface(self, screen_res, camera_width):
        scale_ratio = screen_res.x / camera_width * self.width
        material_res = Vector(self.__texture.get_width(), self.__texture.get_height())
        scaled_material_surface = pygame.transform.scale(self.__texture, (scale_ratio, scale_ratio * material_res.y / material_res.x))
        self.__scaled_material_res = Vector(scaled_material_surface.get_width(), scaled_material_surface.get_height())

        x_tiles = math.ceil(screen_res.x / self.__scaled_material_res.x) + 1
        y_tiles = math.ceil(screen_res.y / self.__scaled_material_res.y) + 1
        
        bg_surface = pygame.Surface((Vector(x_tiles, y_tiles) * self.__scaled_material_res).tuple)

        for x in range(x_tiles):
            for y in range(y_tiles):
                bg_surface.blit(scaled_material_surface, (x * self.__scaled_material_res.x, y * self.__scaled_material_res.y))

        self.__bg_surface = bg_surface


    def get_bg_surface(self, camera_pos, screen_res, camera_width):
        if not screen_res == self.__buffered_screen_res or not camera_width == self.__buffered_camera_width:
            self.__set_buffer(screen_res, camera_width)
            self.__create_bg_surface(screen_res, camera_width)

        top_left = (camera_pos * self.scroll_speed) % self.__scaled_material_res
        if top_left.x < 0:
            top_left.x += self.__scaled_material_res.x
        if top_left.y < 0:
            top_left.y += self.__scaled_material_res.y

        bg_surface = pygame.Surface(screen_res.tuple)
        bg_surface.blit(self.__bg_surface, top_left.tuple)

        return bg_surface



class Background:
    def __init__(self, name, layers):
        self.name = name
        self.__layers = []

        for layer in layers:
            self.add_layer(layer, len(self.__layers))


    @property
    def name(self):
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string.")


    @property
    def layers(self):
        return self.__layers
    

    def add_layer(self, background_layer, index):
        if isinstance(background_layer, BackgroundLayer) and isinstance(index, int) and 0 <= index < len(self.__layers) + 1:
            self.__layers.insert(index, background_layer)
        else:
            raise TypeError("Layer must be a BackgroundLayer instance and index must be an integer in range:", background_layer, index)


    def get_bg_surface(self, camera_pos, screen_res, camera_width):
        bg_surface = pygame.Surface(screen_res.tuple)

        for layer in self.__layers:
            bg_surface.blit(layer.get_bg_surface(camera_pos, screen_res, camera_width), (0, 0))

        return bg_surface
        

