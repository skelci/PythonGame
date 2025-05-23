"""
This module contains the Background and BackgroundLayer classes.
"""

from engine.datatypes import *
from engine.components.material import Material

#?ifdef CLIENT
import pygame
#?endif



class BackgroundLayer:
    """
    Represents a layer in the background. It is a material that can be scrolled at a specific speed.
    The layer can be used to create a parallax effect in the background.
    """
    
    def __init__(self, material: Material, width: float, scroll_speed: float):
        """
        Args:
            material: Material to be used for the layer.
            width: Width of the material in world units.
            scroll_speed: Speed at which the layer scrolls. A value of 1 means it scrolls at the same speed as the camera.
        """
        self.material = material
        self.width = width
        self.scroll_speed = scroll_speed
        self.render_layer = 0

        # self.__buffered_screen_res = None
        # self.__buffered_camera_width = None


    @property
    def material(self):
        """ Material - Material to be used for the layer. """
        return self.__material
    

    @material.setter
    def material(self, value):
        if value.__class__.__name__ == "Material":
            self.__material = value
        else:
            raise TypeError("Texture must be a Material instance.")
        

    @property
    def width(self):
        """ float - Width of the material in world units. """
        return self.__width
    

    @width.setter
    def width(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__width = value
        else:
            raise TypeError("Width must be a positive number.")
        

    @property
    def scroll_speed(self):
        """ float - Speed at which the layer scrolls. A value of 1 means it scrolls at the same speed as the camera. """
        return self.__scroll_speed
    

    @scroll_speed.setter
    def scroll_speed(self, value):
        if isinstance(value, (int, float)):
            self.__scroll_speed = value
        else:
            raise TypeError("Scroll speed must be a number.")
        

    @property
    def render_layer(self):
        """ int - Render layer of the background. """
        return self.__render_layer
    

    @render_layer.setter
    def render_layer(self, value):
        if isinstance(value, int):
            self.__render_layer = value
        else:
            raise TypeError("Render layer must be an integer.")
        

    # def __set_buffer(self, screen_res, camera_width):
    #     self.__buffered_screen_res = screen_res
    #     self.__buffered_camera_width = camera_width
        

    # def __create_bg_surface(self, screen_res, camera_width):
    #     scale_ratio = screen_res.x / camera_width * self.width
    #     material_res = Vector(self.__texture.get_width(), self.__texture.get_height())
    #     scaled_material_surface = pygame.transform.scale(self.__texture, (scale_ratio, scale_ratio * material_res.y / material_res.x))
    #     self.__scaled_material_res = Vector(scaled_material_surface.get_width(), scaled_material_surface.get_height())

    #     x_tiles = math.ceil(screen_res.x / self.__scaled_material_res.x) + 1
    #     y_tiles = math.ceil(screen_res.y / self.__scaled_material_res.y) + 1
        
    #     bg_surface = pygame.Surface((Vector(x_tiles, y_tiles) * self.__scaled_material_res).tuple)

    #     for x in range(x_tiles):
    #         for y in range(y_tiles):
    #             bg_surface.blit(scaled_material_surface, (x * self.__scaled_material_res.x, y * self.__scaled_material_res.y))

    #     self.__bg_surface = bg_surface


    # def get_bg_surface(self, _camera_pos: Vector, screen_res: Vector, camera_width: float):
    #     """
    #     Returns the background surface for the layer.
    #     Args:
    #         _camera_pos: Position of the camera in world units.
    #         screen_res: Resolution of the screen in pixels.
    #         camera_width: Width of the camera in world units.
    #     Returns:
    #         pygame.Surface - Background surface for the layer.
    #     """
    #     if not screen_res == self.__buffered_screen_res or not camera_width == self.__buffered_camera_width:
    #         self.__set_buffer(screen_res, camera_width)
    #         self.__create_bg_surface(screen_res, camera_width)

    #     camera_pos = Vector(-_camera_pos.x, _camera_pos.y)

    #     top_left = (camera_pos * self.scroll_speed * screen_res.x / camera_width) % self.__scaled_material_res - self.__scaled_material_res
    #     if top_left.abs.x > self.__scaled_material_res.x:
    #         top_left.x += self.__scaled_material_res.x
    #     if top_left.abs.y > self.__scaled_material_res.y:
    #         top_left.y += self.__scaled_material_res.y

    #     bg_surface = pygame.Surface(screen_res.tuple)
    #     bg_surface.blit(self.__bg_surface, top_left.tuple)

    #     return bg_surface



class Background:
    """
    Represents the background of the game. It is a collection of BackgroundLayer instances.
    The layers are drawn in the order they are added, with the first layer being drawn first.
    """

    def __init__(self, name: str, layers: list[BackgroundLayer]):
        """
        Args:
            name: Name of the background.
            layers: List of BackgroundLayer instances to be used in the background.
        """
        self.name = name
        self.__layers = []

        for i, layer in enumerate(layers):
            if not isinstance(layer, BackgroundLayer):
                raise TypeError("Layer must be a BackgroundLayer instance:", layer)
            layer.render_layer = i - 512
            self.__layers.append(layer)


    @property
    def name(self):
        """ str - Name of the background. """
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string.")


    @property
    def layers(self):
        """ list[BackgroundLayer] - List of BackgroundLayer instances in the background. """
        return self.__layers
    


