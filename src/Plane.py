from Actor import Actor
from Datatypes import *

import pygame

class Plane(Actor):
    def __init__(self, name, side_length, texture):
        super().__init__(name, texture)
        self.side_length = side_length
        self.texture = pygame.image.load(texture)

        self.create_triangles()


    def create_triangles(self):
        sl = self.side_length
        vertices = (
            Vector(-sl,  sl, 0),
            Vector(-sl, -sl, 0),
            Vector( sl, -sl, 0),
            Vector( sl,  sl, 0)
        )

        self.triangles = self.get_triangles_from_vertices(vertices)
        
