from Datatypes import *

import pygame



class Actor:
    def __init__(self, name, texture):
        self.name = name
        self.texture = pygame.image.load(texture)
        self.vertices = None # list of int (indexes of vertices)
        self.uv_map = None # tuple of int (indexes of uv_map)
        self.triangles = None # list of Triangles
        self.position = Vector(0)
        self.rotation = Rotator(0)


    def rotate(self, rotator):
        self.rotation += rotator
        for i in range(len(self.vertices)):
            self.vertices[i].rotate(rotator)

        return self


    def move(self, vector):
        self.position += vector
        for i in range(len(self.vertices)):
            self.vertices[i] += vector

        return self

