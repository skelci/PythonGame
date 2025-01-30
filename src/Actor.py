from Datatypes import *

import pygame



class Actor:
    def __init__(self, name, texture):
        self.name = name
        self.texture = pygame.image.load(texture)
        self.vertices = None # tuple of int (indexes of vertices)
        self.uv_map = None # tuple of int (indexes of uv_map)
        self.triangles = None # tuple of Triangles
        self.position = Vector(0)
        self.rotation = Rotator(0)


    def rotate(self, rotator):
        self.rotation += rotator
        for v in self.vertices:
            v.rotate(rotator)

        return self


    def move(self, vector):
        self.position += vector
        for v in self.vertices:
            v += vector

        return self

