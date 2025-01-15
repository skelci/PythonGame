from Actor import Actor
from Datatypes import *

import pygame

class Cube(Actor):
    def __init__(self, name, side_length, texture):
        super().__init__(name)
        self.side_length = side_length
        self.texture = pygame.image.load(texture)

        self.create_triangles()


    def create_triangles(self):
        sl = self.side_length
        vertices = (
            Vector(-sl,  sl, -sl),
            Vector(-sl, -sl, -sl),
            Vector( sl, -sl, -sl),
            Vector( sl,  sl, -sl),
            Vector(-sl,  sl,  sl),
            Vector(-sl, -sl,  sl),
            Vector( sl, -sl,  sl),
            Vector( sl,  sl,  sl)
        )

        # Will mybe need to change the order of the vertices ...
        self.triangles = (
            *self.get_triangles_from_vertices(vertices[0:4]),
            *self.get_triangles_from_vertices(vertices[4:8]),
            *self.get_triangles_from_vertices((vertices[0], vertices[3], vertices[4], vertices[7])),
            *self.get_triangles_from_vertices((vertices[2], vertices[3], vertices[6], vertices[7])),
            *self.get_triangles_from_vertices((vertices[1], vertices[2], vertices[5], vertices[6])),
            *self.get_triangles_from_vertices((vertices[0], vertices[1], vertices[4], vertices[5]))
        )
        
