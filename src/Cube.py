from Plane import Plane
from Datatypes import *

import pygame



class Cube(Plane):
    def __init__(self, name, x_half_lenght, y_half_lenght, z_half_lenght, texture):
        self.str_texture = texture
        self.z_half_lenght = z_half_lenght
        super().__init__(name, x_half_lenght, y_half_lenght, texture)

    
    def create_triangles(self):
        plane = Plane(self.name, self.x_half_length, self.y_half_length, self.str_texture)
        top_plane = plane.move(Vector(0, 0, self.z_half_lenght))
        bottom_plane = plane.move(Vector(0, 0, -self.z_half_lenght) * 2)
        
        self.vertices = (
            *top_plane.vertices,
            *bottom_plane.vertices,
        )

        self.uv_map = plane.uv_map

        self.triangles = (
            *top_plane.triangles, # top

            CompactTriangle((4, 5, 0), self.texture, (2, 3, 0)), # back
            CompactTriangle((0, 5, 2), self.texture, (1, 3, 0)),

            CompactTriangle((5, 6, 1), self.texture, (2, 3, 1)), #left
            CompactTriangle((1, 6, 2), self.texture, (1, 3, 0)),

            CompactTriangle((2, 6, 7), self.texture, (1, 2, 3)), # front
            CompactTriangle((2, 7, 3), self.texture, (1, 3, 0)),

            CompactTriangle((3, 7, 4), self.texture, (1, 2, 3)), # right
            CompactTriangle((3, 4, 0), self.texture, (1, 3, 0)),

            CompactTriangle((4, 5, 6), self.texture, (0, 1, 2)), # bottom
            CompactTriangle((4, 6, 7), self.texture, (0, 2, 3))
        )

