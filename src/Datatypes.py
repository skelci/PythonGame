from dataclasses import dataclass
from typing import Iterator
import pygame
import math



pi = math.pi



@dataclass
class Rotator:
    pitch: float = 0
    yaw: float = 0
    roll: float = 0


    def set_degrees(self, pitch, yaw, roll):
        self.pitch = math.radians(pitch)
        self.yaw = math.radians(yaw)
        self.roll = math.radians(roll)

        return self


    def __iter__(self) -> Iterator[float]:
        yield self.pitch
        yield self.yaw
        yield self.roll


    def __add__(self, other):
        if isinstance(other, Rotator):
            return Rotator(
                pitch=self.pitch + other.pitch,
                yaw=self.yaw + other.yaw,
                roll=self.roll + other.roll
            )
        
        elif isinstance(other, (int, float)):
            return Rotator(
                pitch=self.pitch + other,
                yaw=self.yaw + other,
                roll=self.roll + other
            )
        
        return NotImplemented


    def __sub__(self, other):
        if isinstance(other, Rotator):
            return Rotator(
                pitch=self.pitch - other.pitch,
                yaw=self.yaw - other.yaw,
                roll=self.roll - other.roll
            )
        
        elif isinstance(other, (int, float)):
            return Rotator(
                pitch=self.pitch - other,
                yaw=self.yaw - other,
                roll=self.roll - other
            )
        
        return NotImplemented
    
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Rotator(
                pitch=self.pitch * scalar,
                yaw=self.yaw * scalar,
                roll=self.roll * scalar
            )
        
        return NotImplemented
    
    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero.")
            return Rotator(
                pitch=self.pitch / scalar,
                yaw=self.yaw / scalar,
                roll=self.roll / scalar
            )
        
        return NotImplemented



@dataclass
class Vector:
    x: float = 0
    y: float = 0
    z: float = 0


    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z


    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(
                x=self.x + other.x,
                y=self.y + other.y,
                z=self.z + other.z
            )
        
        elif isinstance(other, Vector2):
            return Vector(
                x=self.x + other.x,
                y=self.y + other.y,
                z=self.z
            )
        
        elif isinstance(other, (int, float)):
            return Vector(
                x=self.x + other,
                y=self.y + other,
                z=self.z + other
            )
        
        return NotImplemented


    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(
                x=self.x - other.x,
                y=self.y - other.y,
                z=self.z - other.z
            )
        
        elif isinstance(other, Vector2):
            return Vector(
                x=self.x - other.x,
                y=self.y - other.y,
                z=self.z
            )
        
        elif isinstance(other, (int, float)):
            return Vector(
                x=self.x - other,
                y=self.y - other,
                z=self.z - other
            )
        
        return NotImplemented


    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(
                x=self.x * scalar,
                y=self.y * scalar,
                z=self.z * scalar
            )
        
        return NotImplemented


    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=self.x / scalar,
                y=self.y / scalar,
                z=self.z / scalar
            )
        
        return NotImplemented
    

    @property
    def lenght(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    

    @property
    def lenght_xy(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    

    # Rotate a 3D point around the origin (don't try to understand this)
    def rotate(self, rot):
        # Assume rot.pitch, rot.yaw, rot.roll are in radians
        px, py, pz = self.x, self.y, self.z
        cosx, sinx = math.cos(rot.pitch), math.sin(rot.pitch)
        cosy, siny = math.cos(rot.yaw), math.sin(rot.yaw)
        cosz, sinz = math.cos(rot.roll), math.sin(rot.roll)

        # Rotate around X-axis
        py, pz = py * cosx - pz * sinx, py * sinx + pz * cosx
        # Rotate around Y-axis
        px, pz = px * cosy + pz * siny, -px * siny + pz * cosy
        # Rotate around Z-axis
        px, py = px * cosz - py * sinz, px * sinz + py * cosz

        self.x, self.y, self.z = px, py, pz



@dataclass
class Vector2:
    x: float = 0
    y: float = 0

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y


    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(
                x=self.x + other.x,
                y=self.y + other.y
            )
        
        elif isinstance(other, Vector):
            return Vector(
                x=self.x + other.x,
                y=self.y + other.y,
                z=other.z
            )
        
        elif isinstance(other, (int, float)):
            return Vector2(
                x=self.x + other,
                y=self.y + other
            )
        
        return NotImplemented


    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(
                x=self.x - other.x,
                y=self.y - other.y
            )
        
        elif isinstance(other, Vector):
            return Vector(
                x=self.x - other.x,
                y=self.y - other.y,
                z=other.z
            )
        
        elif isinstance(other, (int, float)):
            return Vector2(
                x=self.x - other,
                y=self.y - other
            )
        
        return NotImplemented


    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector2(
                x=self.x * scalar,
                y=self.y * scalar
            )
        
        return NotImplemented


    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector2(
                x=self.x / scalar,
                y=self.y / scalar
            )
        
        return NotImplemented
    
    @property
    def lenght(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


"""
vertices and uv_map are indexes of the vertices and uv_map in the actor's vertices and uv_map
"""
@dataclass
class CompactTriangle:
    vertices: tuple[int, int, int]
    texture: pygame.Surface
    uv_map: tuple[int, int, int]



@dataclass
class Triangle:
    vertices: list[Vector, Vector, Vector]
    texture: pygame.Surface
    uv_map: tuple[Vector2, Vector2, Vector2]
