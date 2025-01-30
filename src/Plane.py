from Actor import Actor
from Datatypes import *

import pygame

class Plane(Actor):
    def __init__(self, name, x_half_length, y_half_lenght, texture):
        super().__init__(name, texture)
        self.x_half_length = x_half_length
        self.y_half_length = y_half_lenght

        self.create_triangles()


    def create_triangles(self):
        xhl = self.x_half_length
        yhl = self.y_half_length
        self.vertices = [
            Vector( xhl,  yhl, 0),
            Vector(-xhl,  yhl, 0),
            Vector(-xhl, -yhl, 0),
            Vector( xhl, -yhl, 0)
        ]

        self.uv_map = (
            Vector2(1, 1),
            Vector2(0, 1),
            Vector2(0, 0),
            Vector2(1, 0)
        )

        self.triangles = (
            CompactTriangle((0, 1, 2), self.texture, (0, 1, 2)),
            CompactTriangle((0, 2, 3), self.texture, (0, 2, 3))
        )

        return self.vertices, self.uv_map, self.triangles
        
