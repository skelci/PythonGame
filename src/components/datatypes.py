from dataclasses import dataclass
from enum import IntEnum
from typing import Iterator
import math



@dataclass
class Vector:
    x: float = 0
    y: float = 0


    def __post_init__(self):
        if not isinstance(self.x, (int, float)):
            raise TypeError(f"x must be an int or float, got {self.x.__class__.__name__}")
        if not isinstance(self.y, (int, float)):
            raise TypeError(f"y must be an int or float, got {self.y.__class__.__name__}")
        

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
    

    def __floordiv__(self, scalar):
        if isinstance(scalar, Vector):
            if scalar.x == 0 or scalar.y == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=self.x // scalar.x,
                y=self.y // scalar.y
            )
        
        elif isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=self.x // scalar,
                y=self.y // scalar
            )
        
        return NotImplemented
    

    def __mod__(self, scalar):
        if isinstance(scalar, Vector):
            if scalar.x == 0 or scalar.y == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=self.x % scalar.x,
                y=self.y % scalar.y
            )
        
        elif isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=self.x % scalar,
                y=self.y % scalar
            )
        
        return NotImplemented
    

    def __neg__(self):
        return Vector(
            -self.x,
            -self.y
        )
    

    def __hash__(self):
        return hash(self.tuple)

    
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
    def floored(self):
        return Vector(
            math.floor(self.x),
            math.floor(self.y)
        )
    

    @property
    def ceiled(self):
        return Vector(
            math.ceil(self.x),
            math.ceil(self.y)
        )
    

    @property
    def tuple(self):
        return (self.x, self.y)
    

    @property
    def copy(self):
        return Vector(*self)
    

    def dot(self, other):
        if not isinstance(other, Vector):
            raise TypeError(f"other must be a Vector, got {other.__class__.__name__}")
        
        return self.x * other.x + self.y * other.y
    

    def squared_distance(self, other):
        if not isinstance(other, Vector):
            raise TypeError(f"other must be a Vector, got {other.__class__.__name__}")
        
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
    

    def distance(self, other):        
        return self.squared_distance(other) ** 0.5
    

    def manhattan_distance(self, other):
        if not isinstance(other, Vector):
            raise TypeError(f"other must be a Vector, got {other.__class__.__name__}")

        return abs(self.x - other.x) + abs(self.y - other.y)
    


@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255


    def __post_init__(self):
        if not isinstance(self.r, (int, float)) and self.r < 0:
            raise TypeError(f"r must be a positive float, got {self.r}")
        if not isinstance(self.g, (int, float)) and self.g < 0:
            raise TypeError(f"g must be a positive float, got {self.g}")
        if not isinstance(self.b, (int, float)) and self.b < 0:
            raise TypeError(f"b must be a positive float, got {self.b}")
        if not isinstance(self.a, (int, float)) and self.a < 0:
            raise TypeError(f"a must be a positive float, got {self.a}")
        

    def __iter__(self) -> Iterator[int]:
        yield self.r
        yield self.g
        yield self.b
        yield self.a


    def __hash__(self):
        return hash(self.tuple)


    @property
    def tuple(self):
        return (self.r, self.g, self.b, self.a)
    

    @property
    def copy(self):
        return Color(*self)
    

    @property
    def normalized(self):
        return Color(
            r=self.r / 255,
            g=self.g / 255,
            b=self.b / 255,
            a=self.a / 255
        )



@dataclass
class CollisionData:
    normal: Vector
    velocity: Vector
    restitution: float
    mass: float
    collided_actor: str



class Alignment(IntEnum):
    TOP_LEFT = 0
    TOP_CENTER = 1
    TOP_RIGHT = 2
    CENTER_LEFT = 3
    CENTER = 4
    CENTER_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_CENTER = 7
    BOTTOM_RIGHT = 8



class KeyPressType(IntEnum):
    TRIGGER = 0
    HOLD = 1
    RELEASE = 2



class Keys(IntEnum):
    MOUSE_LEFT =        1
    MOUSE_MIDDLE =      2
    MOUSE_RIGHT =       3
    MOUSE_SCROLL_UP =   4
    MOUSE_SCROLL_DOWN = 5
    MOUSE_4 =           6
    MOUSE_5 =           7

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
    RIGHT_SHIFT =       303
    LEFT_SHIFT =        304
    CTRL =              306
    ALT =               308



pi = math.pi
gravity = -9.80665
kinda_small_number = 0.001

