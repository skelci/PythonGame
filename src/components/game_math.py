"""
This module contains various math functions and classes used in the game.
"""

from components.datatypes import *



def is_in_screen_rect(top_left: Vector, bottom_right: Vector, point: Vector):
    """
    Check if a point is within the screen rectangle defined by top left and bottom right corners.
    Args:
        top_left: Top left corner of the rectangle.
        bottom_right: Bottom right corner of the rectangle.
        point: Point to check.
    Returns:
        bool - True if the point is within the rectangle, False otherwise.
    """
    return top_left.x < point.x < bottom_right.x and top_left.y < point.y < bottom_right.y



def is_in_rect(bottom_left: Vector, top_right: Vector, point: Vector):
    """
    Check if a point is within the rectangle defined by bottom left and top right corners.
    Args:
        bottom_left: Bottom left corner of the rectangle.
        top_right: Top right corner of the rectangle.
        point: Point to check.
    Returns:
        bool - True if the point is within the rectangle, False otherwise.
    """
    return bottom_left.x < point.x < top_right.x and bottom_left.y < point.y < top_right.y



def is_overlapping_rect(rect1, rect2):
    """
    Check if two rectangles are overlapping. Rectangles must be an objects with attributes position and half_size.
    Args:
        rect1: First rectangle.
        rect2: Second rectangle.
    Returns:
        bool - True if the rectangles are overlapping, False otherwise.
    """
    return all(d > 0 for d in (
        rect1.position.x + rect1.half_size.x - (rect2.position.x - rect2.half_size.x),
        rect2.position.x + rect2.half_size.x - (rect1.position.x - rect1.half_size.x),
        rect1.position.y + rect1.half_size.y - (rect2.position.y - rect2.half_size.y),
        rect2.position.y + rect2.half_size.y - (rect1.position.y - rect1.half_size.y)
    ))



def lerp(a, b, t: float):
    """
    Linear interpolation between two values a and b.
    Args:
        a: Starting value.
        b: Ending value.
        t: Interpolation factor (0 <= t <= 1).
    Returns:
        float - Interpolated value between a and b.
    """
    return a + (b - a) * t



def clamp(value: float, min_value = 0, max_value = 1):
    """
    Clamp a value between min_value and max_value.
    Args:
        value: Value to clamp.
        min_value: Minimum value.
        max_value: Maximum value.
    Returns:
        float - Clamped value.
    """
    return max(min(value, max_value), min_value)



def get_chunk_cords(pos: Vector) -> Vector:
    """
    Get the chunk coordinates of a given position.
    Args:
        pos: Position to get the chunk coordinates for.
    Returns:
        Vector - Chunk coordinates of the position.
    """
    return pos // chunk_size

