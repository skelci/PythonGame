from Datatypes import *
from Actor import Actor

from dataclasses import dataclass
import pygame
import math



@dataclass
class Camera:
    position: Vector
    rotation: Rotator
    fov: float



class Renderer:
    def __init__(self, width, height, title = "Pygame Window"):
        self.width = width
        self.height = height
        self.title = title

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        self.actors_to_draw = []
        self.triangles = []

        self.camera = Camera(Vector(0, 0, 0), Rotator(0, 0, 0), math.radians(90))


    def add_actor_to_draw(self, actor):
        if not issubclass(type(actor), Actor):
            raise Exception("Actor must be a subclass of Actor")
        
        self.actors_to_draw.append(actor)
        


    
    def clear(self):
        self.actors_to_draw = []
        self.triangles = []


    def render(self):
        combined_surface = pygame.Surface((self.width, self.height))

        # for t in self.triangles:
        #     self.triangles.append(Triangle(
        #         ((t.vertices[0] - self.camera.position).rotate(self.camera.rotation),
        #         (t.vertices[1] - self.camera.position).rotate(self.camera.rotation),
        #         (t.vertices[2] - self.camera.position).rotate(self.camera.rotation)),
        #         t.texture
        #     ))

        for a in self.actors_to_draw:
            for v in a.vertices:
                v += self.camera.position
                v.rotate(self.camera.rotation)

            for t in a.triangles:
                # decompress triangle
                self.triangles.append(Triangle(
                    (a.vertices[t.vertices[0]], a.vertices[t.vertices[1]], a.vertices[t.vertices[2]]),
                    t.texture,
                    (a.uv_map[t.uv_map[0]], a.uv_map[t.uv_map[1]], a.uv_map[t.uv_map[2]])
                ))
            
        def avg_y(t):
            return sum(v.y for v in t.vertices)/3


        self.triangles.sort(key = lambda t: avg_y(t), reverse = True)
        
        for triangle in self.triangles:
            if avg_y(triangle) < 0: # if triangle is behind camera
                continue

            screen_cords = []
            px = math.tan(self.camera.fov / 2) * self.width
            py = self.height / self.width * px
            for v in triangle.vertices:
                cord = Vector2()
                cord.y = v.z / v.y * py
                cord.x = v.x / v.y * px
                screen_cords.append(cord)
                pygame.draw.circle(combined_surface, (255, 255, 255), (int(cord.x + self.width / 2), int(cord.y + self.height / 2)), 5)
                print(cord.x + self.width / 2, cord.y + self.height / 2)

            texture = self.create_triangle_texture(((0, 0), (1, 0), (1, 1)), screen_cords, triangle.texture)

            # combined_surface.blit(*texture)

        self.screen.blit(combined_surface, (0, 0))

        pygame.display.flip()


    def create_triangle_texture(self, tex_cords, screen_cords, texture):
        # Denormalize texture coordinates
        tex_width, tex_height = texture.get_size()
        tex_cords = (
            (tex_cords[0][0] * tex_width, tex_cords[0][1] * tex_height),
            (tex_cords[1][0] * tex_width, tex_cords[1][1] * tex_height),
            (tex_cords[2][0] * tex_width, tex_cords[2][1] * tex_height)
        )

        # Compute angle between vectors
        dx1 = tex_cords[1][0] - tex_cords[0][0]
        dy1 = tex_cords[1][1] - tex_cords[0][1]
        dx2 = screen_cords[1].x - screen_cords[0].x
        dy2 = screen_cords[1].y - screen_cords[0].y

        angle1 = math.degrees(math.atan2(dy1, dx1))
        angle2 = math.degrees(math.atan2(dy2, dx2))
        rotation_angle = angle2 - angle1

        # Compute scale factor (based on distance between first two points)
        dist_img = math.hypot(dx1, dy1)
        dist_screen = math.hypot(dx2, dy2)
        scale_factor = dist_screen / dist_img if dist_img else 1

        # Apply transformation
        transformed = pygame.transform.rotozoom(texture, -rotation_angle, scale_factor)

        # Blit at correct position
        pos_x, pos_y = screen_cords[0]
        return transformed, (pos_x, pos_y)
        
