from dataclasses import dataclass
from typing import Iterator
import math



pi = math.pi



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
        if isinstance(scalar, (int, float)):
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
    def lenght(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    

    @property
    def normalized(self):
        if self.lenght == 0:
            return Vector(0, 0)
        
        return self / self.lenght
    

    @property
    def abs(self):
        return Vector(
            abs(self.x),
            abs(self.y)
        )
    

    def rotate(self, rotator):
        x = self.x * math.cos(rotator.roll) - self.y * math.sin(rotator.roll)
        y = self.x * math.sin(rotator.roll) + self.y * math.cos(rotator.roll)
        
        self.x = x
        self.y = y
        
        return self
