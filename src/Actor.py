import pygame

class Actor:
    def __init__(self, name, texture):
        self.name = name
        self.texture = pygame.image.load(texture)

    def get_triangles_from_vertices(self, vertices):
        return (vertices[0], vertices[1], vertices[2]), (vertices[0], vertices[2], vertices[3])

    