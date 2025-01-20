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
            self.triangles.append(Triangle(
                (t.vertices[0] - self.camera.position,
                t.vertices[1] - self.camera.position,
                t.vertices[2] - self.camera.position),
                t.texture
            ))

        self.triangles.sort(key = lambda t: t.vertices[0].lenght(), reverse = True)
        
        for triangle in self.triangles:
            screen_cords = []
            for v in triangle.vertices:
                cord = Vector2()

                k_pitch_camera = math.tan(self.camera.rotation.pitch)
                if k_pitch_camera == 0: k_pitch_per = float('inf')
                else: k_pitch_per = -1 / k_pitch_camera
                x_pitch = v.lenghtXY()
                n_pitch_per = v.z - k_pitch_per * x_pitch
                y_pitch_sec = k_pitch_per * x_pitch
                x_pitch_sec_div = k_pitch_camera - k_pitch_per
                if x_pitch_sec_div == 0: x_pitch_sec = float('inf')
                elif abs(x_pitch_sec_div) == float('inf') and abs(n_pitch_per) == float('inf'):
                    if x_pitch_sec_div * n_pitch_per > 0: x_pitch_sec = 1
                    else: x_pitch_sec = -1
                else: x_pitch_sec = n_pitch_per / x_pitch_sec_div
                cord.y = math.sqrt((v.z - y_pitch_sec)**2 + (x_pitch - x_pitch_sec)**2) * Vector2(y_pitch_sec, x_pitch_sec).lenght()
                k_pitch_sec = y_pitch_sec / x_pitch_sec
                if k_pitch_sec < k_pitch_camera: cord.y = -cord.y
                cord.y += self.height / 2
                
                k_yaw_camera = math.tan(self.camera.rotation.yaw)
                if k_yaw_camera == 0: k_yaw_per = float('inf')
                else: k_yaw_per = -1 / k_yaw_camera
                n_yaw_per = v.y - k_yaw_per * v.x
                y_yaw_sec = k_yaw_camera * v.x
                x_yaw_sec_div = k_yaw_camera - k_yaw_per
                if x_yaw_sec_div == 0: x_yaw_sec = float('inf')
                elif abs(x_yaw_sec_div) == float('inf') and abs(n_yaw_per) == float('inf'):
                    if x_yaw_sec_div * n_yaw_per > 0: 1
                    else: x_yaw_sec = -1
                else: x_yaw_sec = n_yaw_per / x_yaw_sec_div
                cord.x = math.sqrt((v.y - y_yaw_sec)**2 + (v.x - x_yaw_sec)**2) * Vector2(y_yaw_sec, x_yaw_sec).lenght()
                k_yaw_sec = y_yaw_sec / x_yaw_sec
                if k_yaw_sec < k_yaw_camera: cord.x = -cord.x
                cord.x += self.width / 2

                screen_cords.append(cord)

            print(screen_cords)

            texture = self.create_triangle_texture(((0, 0), (1, 0), (1, 1)), screen_cords, triangle.texture)

            combined_surface.blit(*texture)

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
        