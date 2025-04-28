"""
This module defines the Character class, which is used to create a character object in the game.
"""

from .rigidbody import Rigidbody

from .datatypes import *
from .material import Material



class Character(Rigidbody):
    """
    This class represents a character in the game.
    It inherits from the Rigidbody class and adds functionality for character movement and jumping.
    """

    #                                                                                                                                                                                                                                                             why the f does this bastard of Vector(0, 0) return a new vector object, but Vector() returns the fucking reference to some other vector object? I don't get it. I don't get it at all
    def __init__(self, name: str, position = Vector(), half_size = Vector(0.4, 0.8), generate_overlap_events = True, collidable = True, simulate_physics = True, visible = True, material: Material = None, render_layer = 1, restitution = 0, initial_velocity = Vector(0, 0), min_velocity = KINDA_SMALL_NUMBER, mass = 70, gravity_scale = 1, air_resistance = 0.1, deceleration = 10, jump_velocity = 6, walk_speed = 3, acceleration = 6, air_control = 0.2):
        """
        Refer to the Rigidbody class for more information about the parameters.
        Args:
            jump_velocity: Y velocity when jumping. Default is 6.
            walk_speed: Maximum X velocity when walking. Default is 3.
            acceleration: Acceleration when moving. Default is 6.
            air_control: Precentage of walk speed that can be controlled in the air. Default is 0.2.
        """
        super().__init__(name, position, half_size, generate_overlap_events, collidable, simulate_physics, visible, material, render_layer, restitution, initial_velocity, min_velocity, mass, gravity_scale, air_resistance, deceleration)
        
        self.jump_velocity = jump_velocity
        self.walk_speed = walk_speed
        self.acceleration = acceleration
        self.air_control = air_control
        self.move_direction = 0


    @property
    def jump_velocity(self):
        """ float - Y velocity when jumping. """
        return self.__jump_velocity
    

    @jump_velocity.setter
    def jump_velocity(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__jump_velocity = value
        else:
            raise TypeError("Jump velocity must be a positive float:", value)
        

    @property
    def walk_speed(self):
        """ float - Maximum X velocity when walking. """
        return self.__walk_speed
    

    @walk_speed.setter
    def walk_speed(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__walk_speed = value
        else:
            raise TypeError("Walk speed must be a positive float:", value)
        

    @property
    def acceleration(self):
        """ float - Acceleration when moving. """
        return self.__acceleration
    

    @acceleration.setter
    def acceleration(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__acceleration = value
        else:
            raise TypeError("Acceleration must be a positive float:", value)
        

    @property
    def air_control(self):
        """ float - Percentage of walk speed that can be controlled in the air. """
        return self.__air_control
    

    @air_control.setter
    def air_control(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__air_control = value
        else:
            raise TypeError("Air control must be a positive float:", value)
        

    @property
    def move_direction(self):
        """ int - Direction of movement. -1 for left, 0 for no movement, 1 for right. """
        return self.__move_direction
    

    @move_direction.setter
    def move_direction(self, value):
        if isinstance(value, int) and value in (-1, 0, 1):
            self.__move_direction = value
        else:
            raise TypeError("Move direction must be -1, 0 or 1:", value)
        

    def jump(self):
        """ Makes the character jump. The character can only jump if it is on the ground. """
        if self.is_grounded:
            self.velocity.y = self.jump_velocity


    def __move(self, delta_time):
        direction = self.move_direction
        dad = direction * self.acceleration * delta_time
        if self.velocity.abs.x < self.walk_speed:
            if self.is_grounded:
                self.velocity.x += dad
                if self.velocity.abs.x > self.walk_speed:
                    self.velocity.x -= self.walk_speed * dad
                    if self.velocity.abs.x < self.walk_speed:
                        self.velocity.x = direction * self.walk_speed
            else:
                wa = self.walk_speed * self.air_control
                self.velocity.x += self.air_control * dad
                if self.velocity.abs.x > wa:
                    self.velocity.x -= wa * self.air_resistance * dad
                    if self.velocity.abs.x < wa:
                        self.velocity.x = direction * wa

        self.move_direction = 0


    def tick(self, delta_time: float):
        """
        Updates the character's velocity and position.
        Args:
            delta_time: Time since the last tick.
        """
        self.position += self.velocity * delta_time
        
        # Min velocity
        if self.velocity.abs.x < self.min_velocity:
            self.velocity.x = 0
        if self.velocity.abs.y < self.min_velocity:
            self.velocity.y = 0

        # Gravity
        if not self.is_grounded and self.simulate_physics:
            self.velocity.y += GRAVITY * self.gravity_scale * delta_time

        # Air resistance
        v_change = self.velocity * self.air_resistance * delta_time
        if self.velocity.length < v_change.length:
            self.velocity = Vector(0, 0)
        else:
            self.velocity -= v_change

        # Friction
        if self.is_grounded and self.move_direction == 0:
            v_change = self.deceleration * delta_time
            if self.velocity.abs.x <= v_change:
                self.velocity.x = 0
            else:
                self.velocity.x -= v_change * self.velocity.x / self.velocity.abs.x

        self.__move(delta_time)





