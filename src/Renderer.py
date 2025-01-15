from Datatypes import *

from dataclasses import dataclass
import pygame
import math



@dataclass
class Triangle:
    vertices: tuple[Vector, Vector, Vector]
    texture: pygame.image



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

        self.triangles = []

        self.camera = Camera(Vector(0, 0, 0), Rotator(0, 0, 0), math.radians(90))


    def add_actor_to_draw(self, actor):
        if actor.triangles is None:
            raise Exception(f"Actor {actor.name} has no triangles to render")
        
        for triangle in actor.triangles:
            self.triangles.append(Triangle(triangle, actor.texture))

    
    def clear(self):
        self.triangles.clear()


    def render(self):
        combined_surface = pygame.Surface((self.width, self.height))

        triengles = self.triangles.copy()
        for t in triengles:
            Triangle(
                (Vector(t.vertices[0] - self.camera.position),
                Vector(t.vertices[1] - self.camera.position),
                Vector(t.vertices[2] - self.camera.position)),
                t.texture
            )

        self.triangles.sort(key = lambda t: t.vertices[0].lenght())
        
        for triangle in self.triangles:
            screen_cords = []
            out_of_view = 0
            for v in triangle.vertices:
                angle = Rotator(math.atan2(v.z, v.lenghtXY()), math.atan2(v.y, v.x), 0)
                angle -= self.camera.rotation
                if -self.camera.fov/2 < angle.pitch < self.camera.fov/2 or -self.camera.fov/2 < angle.yaw < self.camera.fov/2: out_of_view += 1
                cord = Vector2(math.sin(angle.yaw) * self.width + self.width/2, math.sin(angle.pitch) * self.height + self.height/2)
                screen_cords.append(cord)
            if out_of_view == 3: continue

            texture = self.create_triangle_texture(((0, 0), (1, 0), (1, 1)), screen_cords, triangle.texture)

            combined_surface.blit(texture[0], texture[1])

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
        