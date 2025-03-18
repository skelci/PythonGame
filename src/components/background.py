from components.datatypes import *
from engine.gl_wrapper import *

import pygame 



class BackgroundLayer:
    def __init__(self, material, width, scroll_speed):
        self.material = material
        self.width = width
        self.scroll_speed = scroll_speed


    @property
    def material(self):
        return self.__material
    

    @material.setter
    def material(self, value):
        if value.__class__.__name__ == "Material":
            self.__material = value
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
    

    def draw_bg_surface(self, camera_pos, screen_res, camera_width):
        scale_ratio = screen_res.x / camera_width * self.width
        material_res = Vector(*self.__material.texture.get_size())
        scaled_material_res = Vector(scale_ratio, scale_ratio * material_res.y / material_res.x)

        x_tiles, y_tiles = (screen_res / scaled_material_res).ceiled + 1
        
        draw_batch = QuadBatch()

        bg_offset = -camera_pos * self.scroll_speed * screen_res.x / camera_width % scaled_material_res - scaled_material_res
        if bg_offset.abs.x > scaled_material_res.x:
            bg_offset.x += scaled_material_res.x
        if bg_offset.abs.y > scaled_material_res.y:
            bg_offset.y += scaled_material_res.y

        for x in range(x_tiles):
            for y in range(y_tiles):
                bottom_right = Vector(x, y) * scaled_material_res + bg_offset
                draw_batch.add_quad(*bottom_right, *scaled_material_res)

        draw_batch.upload()
        draw_batch.draw_batch(self.__material.texture_id)



class Background:
    def __init__(self, name, layers = []):
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


    def draw_bg_surface(self, camera_pos, screen_res, camera_width):
        for layer in self.__layers:
            layer.draw_bg_surface(camera_pos, screen_res, camera_width)
        

