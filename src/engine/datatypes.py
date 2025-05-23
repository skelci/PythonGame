"""
This module contains various data types, utility classes, enums, and constants used in the game.
"""

from pygame import Vector2

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterator
import math
from collections import deque
from queue import Queue
import threading



class Vector(Vector2):
    @staticmethod
    def from_tuple(tup):
        """ Creates a Vector instance from a tuple of x and y coordinates. """
        if not isinstance(tup, tuple) or len(tup) != 2:
            raise TypeError("Expected a tuple of two elements.")
        
        return Vector(*tup)


    def __add__(self, other):
        if isinstance(other, tuple):
            other = self.from_tuple(other)

        if isinstance(other, Vector):
            return super().__add__(other)

        elif isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other)
        
        return NotImplemented
    
    __radd__ = __add__


    def __sub__(self, other):
        if isinstance(other, tuple):
            other = self.from_tuple(other)

        if isinstance(other, Vector):
            return super().__sub__(other)
        
        elif isinstance(other, (int, float)):
            return Vector(self.x - other, self.y - other)
        
        return NotImplemented
    
    
    def __rsub__(self, other):
        if isinstance(other, tuple):
            other = self.from_tuple(other)

        if isinstance(other, Vector):
            return other.__sub__(self)
        
        elif isinstance(other, (int, float)):
            return Vector(other - self.x, other - self.y)
        
        return NotImplemented
    

    def __mul__(self, scalar):
        if isinstance(scalar, tuple):
            scalar = self.from_tuple(scalar)

        if isinstance(scalar, Vector2):
            return Vector(self.x * scalar.x, self.y * scalar.y)

        result = super().__mul__(scalar)
        if isinstance(result, Vector2):
            return Vector(result.x, result.y)
        return NotImplemented

    __rmul__ = __mul__


    def __mod__(self, scalar):
        if isinstance(scalar, tuple):
            scalar = self.from_tuple(scalar)

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
    

    def __rmod__(self, scalar):
        if isinstance(scalar, tuple):
            scalar = self.from_tuple(scalar)

        if isinstance(scalar, Vector):
            return scalar.__mod__(self)
        
        elif isinstance(scalar, (int, float)):
            if self.x == 0 or self.y == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(
                x=scalar % self.x,
                y=scalar % self.y
            )
        
        return NotImplemented


    def __truediv__(self, scalar):
        if isinstance(scalar, tuple):
            scalar = self.from_tuple(scalar)

        if isinstance(scalar, Vector):
            if scalar.x == 0 or scalar.y == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(self.x / scalar.x, self.y / scalar.y)
        
        elif isinstance(scalar, (int, float)):
            return super().__truediv__(scalar)
        
        return NotImplemented
    

    def __rtruediv__(self, scalar):
        if isinstance(scalar, tuple):
            scalar = self.from_tuple(scalar)

        if isinstance(scalar, Vector):
            return scalar.__truediv__(self)
        
        elif isinstance(scalar, (int, float)):
            return Vector(scalar / self.x, scalar / self.y)
        
        return NotImplemented


    def __floordiv__(self, scalar):
        if isinstance(scalar, tuple):
            scalar = self.from_tuple(scalar)

        if isinstance(scalar, Vector):
            if scalar.x == 0 or scalar.y == 0:
                raise ValueError("Cannot divide by zero.")
            return Vector(self.x // scalar.x, self.y // scalar.y)
        
        elif isinstance(scalar, (int, float)):
            return super().__floordiv__(scalar)
        
        return NotImplemented
    
    
    def __rfloordiv__(self, scalar):
        if isinstance(scalar, tuple):
            scalar = self.from_tuple(scalar)

        if isinstance(scalar, Vector):
            return scalar.__floordiv__(self)

        elif isinstance(scalar, (int, float)):
            return Vector(scalar // self.x, scalar // self.y)


    def __hash__(self):
        return hash(self.tuple)
    

    @property
    def length(self):
        return super().length()
    

    @property
    def normalized(self):
        if self.length == 0:
            return Vector(0, 0)
        return super().normalize()
    

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
    def max(self):
        """ float - The maximum value of the vector's x and y components. """
        return max(self.x, self.y)
    

    @property
    def min(self):
        """ float - The minimum value of the vector's x and y components. """
        return min(self.x, self.y)
    

    @property
    def int(self):
        """ Vector - The vector with x and y components converted to integers. """
        return (int(self.x), int(self.y))
    

    @property
    def tuple(self):
        """ tuple[float, float] - The vector as a tuple of x and y components. """
        return (self.x, self.y)
    

    @property
    def copy(self):
        return super().copy()
    


@dataclass
class Color:
    """ Represents a color with red, green, blue, and alpha channels. """
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255


    def __post_init__(self):
        if not isinstance(self.r, (int, float)) and not 255 >= self.r >= 0:
            raise TypeError(f"r must be a positive float, got {self.r}")
        if not isinstance(self.g, (int, float)) and not 255 >= self.g >= 0:
            raise TypeError(f"g must be a positive float, got {self.g}")
        if not isinstance(self.b, (int, float)) and not 255 >= self.b >= 0:
            raise TypeError(f"b must be a positive float, got {self.b}")
        if not isinstance(self.a, (int, float)) and not 255 >= self.a >= 0:
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
        """ tuple[int, int, int, int] - The color as a tuple of red, green, blue, and alpha channels. """
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
    """ Represents collision data for a physics engine. """
    normal: Vector
    velocity: Vector
    restitution: float
    mass: float
    collided_actor: str



class AdvancedQueue():
    """ A queue implementation with a fast way to manage more than one element at a time. """

    def __init__(self):
        self.__buffer = Queue()
        self.lock = threading.Lock()


    def add_data(self, data):
        with self.lock:
            self.__buffer.put(data)


    def get_data(self, size = 1):
        data = []
        with self.lock:
            for _ in range(min(size, self.__buffer.qsize())):
                data.append(self.__buffer.get())
        return data
    

    def get_all_data(self):
        data = []
        with self.lock:
            while not self.__buffer.empty():
                data.append(self.__buffer.get())
        return data
    

    def add_data_multiple(self, data_list):
        with self.lock:
            for data in data_list:
                self.__buffer.put(data)


class AdvancedDeque:
    """ A deque implementation with a fast way to get more than one element at a time. """

    def __init__(self):
        self.__front_buffer = deque()
        self.__back_buffer = deque()
        self.lock = threading.Lock()


    def __swap_buffers(self):
        with self.lock:
            self.__front_buffer, self.__back_buffer = self.__back_buffer, self.__front_buffer


    def add_data_front(self, data):
        with self.lock:
            self.__back_buffer.appendleft(data)


    def add_data_back(self, data):
        with self.lock:
            self.__back_buffer.append(data)


    def get_data(self, size = 1):
        self.__swap_buffers()
        buffer_size = len(self.__front_buffer)
        data = []
        for _ in range(min(size, buffer_size)):
            data.append(self.__front_buffer.popleft())

        self.__swap_buffers()
        self.add_data_back_multiple(self.__front_buffer)
        self.__front_buffer.clear()

        return data


    def get_all_data(self):
        self.__swap_buffers()
        data = list(self.__front_buffer)
        self.__front_buffer.clear()
        return data


    def add_data_front_multiple(self, data_list):
        with self.lock:
            for data in reversed(data_list):
                self.__back_buffer.appendleft(data)


    def add_data_back_multiple(self, data_list):
        with self.lock:
            self.__back_buffer.extend(data_list)



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
    """ Integer values representing various keyboard and mouse keys as defined by pygame. """

    MOUSE_LEFT =            1
    MOUSE_MIDDLE =          2
    MOUSE_RIGHT =           3
    MOUSE_SCROLL_UP =       4
    MOUSE_SCROLL_DOWN =     5
    MOUSE_4 =               6
    MOUSE_5 =               7

    BACKSPACE =             8
    TAB =                   9
    ENTER =                 13
    ESC =                   27
    SPACE =                 32
    EXCLAMATION =           33
    QUOTE =                 34
    HASH =                  35
    DOLLAR =                36
    PERCENT =               37
    AMPERSAND =             38
    APOSTROPHE =            39
    BRACKET_LEFT =          40
    BRACKET_RIGHT =         41
    ASTERISK =              42
    PLUS =                  43
    COMMA =                 44
    MINUS =                 45
    DOT =                   46
    SLASH =                 47

    KEY_0 =                 48
    KEY_1 =                 49
    KEY_2 =                 50
    KEY_3 =                 51
    KEY_4 =                 52
    KEY_5 =                 53
    KEY_6 =                 54
    KEY_7 =                 55
    KEY_8 =                 56
    KEY_9 =                 57

    COLON =                 58
    SEMICOLON =             59
    LESS =                  60
    EQUAL =                 61
    GREATER =               62
    QUESTION =              63
    AT =                    64
    SQUARE_BRACKET_LEFT =   91
    BACKSLASH =             92
    SQUARE_BRACKET_RIGHT =  93
    CARET =                 94
    UNDERSCORE =            95
    GRAVE =                 96

    A =                     97
    B =                     98
    C =                     99
    D =                     100
    E =                     101
    F =                     102
    G =                     103
    H =                     104
    I =                     105
    J =                     106
    K =                     107
    L =                     108
    M =                     109
    N =                     110
    O =                     111
    P =                     112
    Q =                     113
    R =                     114
    S =                     115
    T =                     116
    U =                     117
    V =                     118
    W =                     119
    X =                     120
    Y =                     121
    Z =                     122

    CURLY_BRACKET_LEFT =    123
    PIPE =                  124
    CURLY_BRACKET_RIGHT =   125
    TILDE =                 126
    DELETE =                127

    F1 =                    1073741882
    F2 =                    1073741883
    F3 =                    1073741884
    F4 =                    1073741885
    F5 =                    1073741886
    F6 =                    1073741887
    F7 =                    1073741888
    F8 =                    1073741889
    F9 =                    1073741890
    F10 =                   1073741891
    F11 =                   1073741892
    F12 =                   1073741893
    HOME =                  1073741898
    PAGE_UP =               1073741899
    END =                   1073741901
    PAGE_DOWN =             1073741902
    RIGHT =                 1073741903
    LEFT =                  1073741904
    DOWN =                  1073741905
    UP =                    1073741906
    LEFT_SHIFT =            1073742049
    CTRL =                  1073742050  # using left Control
    ALT =                   1073742052  # using left Alt
    RIGHT_SHIFT =           1073742053



PI = math.pi
GRAVITY = -9.80665
KINDA_SMALL_NUMBER = 0.001
CHUNK_SIZE = 2



