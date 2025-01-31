from Datatypes import *



class Actor:
    def __init__(self, name, x_half_size = 1, y_half_size = 1, position = Vector(), visible = True, texture = None):
        self.name = name
        self.x_half_size = x_half_size
        self.y_half_size = y_half_size
        self.position = position
        self.visible = visible
        self.texture = texture

        self.create_vertices()


    def move(self, vector):
        self.position += vector
        for i in range(len(self.vertices)):
            self.vertices[i] += vector

        return self
    

    def create_vertices(self):
        self.vertices = [
            Vector(1, 1),
            Vector(-1, 1),
            Vector(-1, -1),
            Vector(1, -1)
        ]

        for i in range(len(self.vertices)):
            self.vertices[i] = self.vertices[i] * Vector(self.x_half_size, self.y_half_size)

        return self


