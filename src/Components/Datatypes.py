from dataclasses import dataclass
from typing import Iterator
import math



pi = math.pi
gravity  = -9.80665
kinda_small_number = 0.0001



@dataclass
class Vector:
    x: float = 0
    y: float = 0


    def __post_init__(self):
        if not isinstance(self.x, (int, float)):
            raise TypeError(f"x must be an int or float, got {type(self.x).__name__}")
        if not isinstance(self.y, (int, float)):
            raise TypeError(f"y must be an int or float, got {type(self.y).__name__}")
        

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y


    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(
                x=self.x + other.x,
                y=self.y + other.y
            )

        
        elif isinstance(other, (int, float)):
            return Vector(
                x=self.x + other,
                y=self.y + other
            )
        
        return NotImplemented


    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(
                x=self.x - other.x,
                y=self.y - other.y
            )
        
        elif isinstance(other, (int, float)):
            return Vector(
                x=self.x - other,
                y=self.y - other
            )
        
        return NotImplemented


    def __mul__(self, scalar):
        if isinstance(scalar, Vector):
            return Vector(
                x=self.x * scalar.x,
                y=self.y * scalar.y
            )
        
        elif isinstance(scalar, (int, float)):
            return Vector(
                x=self.x * scalar,
                y=self.y * scalar
            )
        
        return NotImplemented


    def __truediv__(self, scalar):
        if isinstance(scalar, Vector):
            if scalar.x == 0 or scalar.y == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=self.x / scalar.x,
                y=self.y / scalar.y
            )
        
        elif isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=self.x / scalar,
                y=self.y / scalar
            )
        
        return NotImplemented
    

    def __neg__(self):
        return Vector(
            -self.x,
            -self.y
        )

    
    @property
    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    

    @property
    def normalized(self):
        if self.length == 0:
            return Vector(0, 0)
        
        return self / self.length
    

    @property
    def abs(self):
        return Vector(
            abs(self.x),
            abs(self.y)
        )
    

    @property
    def rounded(self):
        return Vector(
            round(self.x),
            round(self.y)
        )
    

    def dot(self, other):
        if not isinstance(other, Vector):
            raise TypeError(f"other must be a Vector, got {type(other).__name__}")
        
        return self.x * other.x + self.y * other.y
    


@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255


    def __post_init__(self):
        if not isinstance(self.r, int):
            raise TypeError(f"r must be an int, got {type(self.r).__name__}")
        if not isinstance(self.g, int):
            raise TypeError(f"g must be an int, got {type(self.g).__name__}")
        if not isinstance(self.b, int):
            raise TypeError(f"b must be an int, got {type(self.b).__name__}")
        if not isinstance(self.a, int):
            raise TypeError(f"a must be an int, got {type(self.a).__name__}")
        

    def __iter__(self) -> Iterator[int]:
        yield self.r
        yield self.g
        yield self.b
        yield self.a



@dataclass
class CollisionData:
    normal: Vector
    velocity: Vector
    restitution: float
    mass: float
    collided_actor: str

