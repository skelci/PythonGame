from dataclasses import dataclass
from enum import IntEnum
from typing import Iterator
import math



pi = math.pi
gravity  = -9.80665
kinda_small_number = 0.001



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
    

    @property
    def tuple(self):
        return (self.x, self.y)
    

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


    @property
    def tuple(self):
        return (self.r, self.g, self.b, self.a)



@dataclass
class CollisionData:
    normal: Vector
    velocity: Vector
    restitution: float
    mass: float
    collided_actor: str



class Alignment(IntEnum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2



class Key(IntEnum):
    MOUSE_LEFT =        1
    MOUSE_MIDDLE =      2
    MOUSE_RIGHT =       3
    MOUSE_SCROLL_UP =   4
    MOUSE_SCROLL_DOWN = 5

    BACKSPACE =         8
    TAB =               9
    ENTER =             13
    ESC =               27
    SPACE =             32
    KEY_0 =             48
    KEY_1 =             49
    KEY_2 =             50
    KEY_3 =             51
    KEY_4 =             52
    KEY_5 =             53
    KEY_6 =             54
    KEY_7 =             55
    KEY_8 =             56
    KEY_9 =             57
    A =                 97
    B =                 98
    C =                 99
    D =                 100
    E =                 101
    F =                 102
    G =                 103
    H =                 104
    I =                 105
    J =                 106
    K =                 107
    L =                 108
    M =                 109
    N =                 110
    O =                 111
    P =                 112
    Q =                 113
    R =                 114
    S =                 115
    T =                 116
    U =                 117
    V =                 118
    W =                 119
    X =                 120
    Y =                 121
    Z =                 122
    KEY_UP =            273
    KEY_DOWN =          274
    KEY_RIGHT =         275
    KEY_LEFT =          276
    F1 =                282
    F2 =                283
    F3 =                284
    F4 =                285
    F5 =                286
    F6 =                287
    F7 =                288
    F8 =                289
    F9 =                290
    F10 =               291
    F11 =               292
    F12 =               293
    SHIFT =             304
    CTRL =              306
    ALT =               308

