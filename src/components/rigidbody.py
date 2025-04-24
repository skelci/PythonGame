"""
This module contains the Rigidbody class, which is used to create a rigid body physics object.
"""

from components.actor import Actor

from components.material import Material
from components.datatypes import *



class Rigidbody(Actor):
    """
    This class represents a rigid body physics object.
    It is used to create a physics object that can be moved and collided with other objects.
    """
    
    def __init__(self, name: str, position: Vector, half_size = Vector(0.5, 0.5), generate_overlap_events = False, collidable = True, simulate_physics = True, visible = True, material: Material = None, render_layer = 0, restitution = 0.5, initial_velocity = Vector(), min_velocity = KINDA_SMALL_NUMBER, mass = 1, gravity_scale = 1, air_resistance = 0.1, deceleration = 10):
        """
        Refer to the Actor class for more information about the parameters.
        Args:
            simulate_physics: Whether to simulate physics or not. If not, the object will not be affected by gravity, velocity or collisions.
            initial_velocity: Initial velocity of the object. This is a vector that represents the speed and direction of the object.
            min_velocity: Minimum velocity of the object. This is a float that represents the minimum length of the velocity vector. If the length of the velocity vector is less than this value, the velocity will be set to 0.
            mass: Mass of the object. This represents the mass of the object. It is used to calculate new velocity after collision.
            gravity_scale: Gravity scale of the object. This represents the scale of the gravity applied to the object.
            air_resistance: Air resistance of the object. This represents the air resistance applied to the object.
            deceleration: Friction of the object. This represents the friction applied to the object.
        """
        super().__init__(name, position, half_size, generate_overlap_events, collidable, visible, material, render_layer, restitution)

        self.simulate_physics = simulate_physics
        self.velocity = initial_velocity
        self.min_velocity = min_velocity
        self.mass = mass
        self.gravity_scale = gravity_scale
        self.air_resistance = air_resistance
        self.deceleration = deceleration

        self.collided_sides = [0, 0, 0, 0] # right, left, top, bottom


    @property
    def simulate_physics(self):
        """ bool - Whether to simulate physics or not. If not, the object will not be affected by gravity, velocity or collisions. """
        return self.__simulate_physics
    

    @simulate_physics.setter
    def simulate_physics(self, value):
        if isinstance(value, bool):
            self.__simulate_physics = value
        else:
            raise TypeError("Simulate physics must be a boolean:", value)
        

    @property
    def velocity(self):
        """ Vector - Velocity of the object. This is a vector that represents the speed and direction of the object. """
        return self.__velocity
    

    @velocity.setter
    def velocity(self, value):
        if isinstance(value, Vector):
            self.__velocity = value
        else:
            raise TypeError("Velocity must be a Vector:", value)
        

    @property
    def min_velocity(self):
        """ Vector - Minimum velocity of the object. This is a float that represents the minimum length of the velocity vector. If the length of the velocity vector is less than this value, the velocity will be set to 0. """
        return self.__min_velocity
    

    @min_velocity.setter
    def min_velocity(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__min_velocity = value
        else:
            raise TypeError("Min velocity must be a positive float:", value)
        

    @property
    def mass(self):
        """ float - Mass of the object. It is used to calculate new velocity after collision. """
        return self.__mass
    

    @mass.setter
    def mass(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__mass = value
        else:
            raise TypeError("Mass must be a positive float:", value)
        

    @property
    def gravity_scale(self):
        """ float - Gravity scale of the object. """
        return self.__gravity_scale
    

    @gravity_scale.setter
    def gravity_scale(self, value):
        if isinstance(value, (int, float)):
            self.__gravity_scale = value
        else:
            raise TypeError("Gravity scale must be a float:", value)
        

    @property
    def air_resistance(self):
        """ float - Air resistance of the object. This represents the percentage of the velocity that is removed each second. """
        return self.__air_resistance
    

    @air_resistance.setter
    def air_resistance(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__air_resistance = value
        else:
            raise TypeError("Air resistance must be a positive float:", value)
        

    @property
    def deceleration(self):
        """ float - Friction of the object. This represents the value of the x-axis velocity that is removed each second. """
        return self.__deceleration
    

    @deceleration.setter
    def deceleration(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__deceleration = value
        else:
            raise TypeError("Friction must be a positive float:", value)
        

    @property
    def collided_sides(self):
        """ list[int] - List of collided sides. This is a list of 4 integers that represent the distance to the collided side. The order is right, left, top, bottom. If the distance is 0, it means that the object is not colliding with that side. """
        return self.__collided_sides
    

    @collided_sides.setter
    def collided_sides(self, value):
        if isinstance(value, list) and len(value) == 4:
            self.__collided_sides = value
        else:
            raise TypeError("Collided sides must be a list with lenght of 4:", value)
        

    @property
    def is_grounded(self):
        """ bool - Whether the rigidbody is on the ground or not. """
        return self.collided_sides[3] != 0
        

    def on_collision(self, collision_data):
        """
        Refer to the Actor class for more information.
        Calculates the new velocity of the object after a collision.
        """
        # Bounce based on formula: j = v_rel * -(1 + e) / (1 / m1 + 1 / m2)
        v_rel = self.velocity - collision_data.velocity
        e = self.restitution * collision_data.restitution
        j = v_rel * -(1 + e) / (1 / self.mass + 1 / collision_data.mass)
        self.velocity += j / self.mass * collision_data.normal.abs
        

    def tick(self, delta_time):
        """
        Refer to the Actor class for more information.
        Updates the velocity of the object based on the physics simulation.
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
        if self.is_grounded:
            v_change = self.deceleration * delta_time
            if self.velocity.abs.x <= v_change:
                self.velocity.x = 0
            else:
                self.velocity.x -= v_change * self.velocity.x / self.velocity.abs.x


    def is_colliding(self, collided_actor: Actor):
        """
        Checks if the object is colliding with another object.
        Args:
            collided_actor: The actor to check for collision with.
        Returns:
            bool - Whether the object is colliding with the other object or not.
            list[float] - List of distances to the collided side. The order is right, left, top, bottom.
        """
        distances = self.get_edge_distances(collided_actor)
        return (
            all(d > 0 for d in distances),
            distances
        )


    def collision_response_direction(self, collided_actor: Actor):
        """
        Calculates the direction to push the object away from the collided object.
        Args:
            collided_actor: The actor to check for collision with.
        Returns:
            Vector - Direction to push the object away from the collided object.
        """
        is_colliding, distances = self.is_colliding(collided_actor)
        if not is_colliding:
            return Vector(0, 0)

        push_right, push_left, push_up, push_down = distances
        
        min_push = min(push_right, push_left, push_down, push_up)
        
        direction = Vector(0, 0)
        if min_push == push_right:
            direction.x = -push_right
        elif min_push == push_left:
            direction.x = push_left
        elif min_push == push_down:
            direction.y = push_down # idk why but for y axis down is positive
        else:
            direction.y = -push_up
        
        return direction
        

    def get_edge_distances(self, collided_actor: Actor):
        """
        Calculates the distances to the collided sides.
        Args:
            collided_actor: The actor to check for collision with.
        Returns:
            list[float] - List of distances to the collided side. The order is right, left, top, bottom. Negative value means that the object is colliding with that side.
        """
        # right, left, top, bottom
        return (
            self.position.x + self.half_size.x - (collided_actor.position.x - collided_actor.half_size.x),
            collided_actor.position.x + collided_actor.half_size.x - (self.position.x - self.half_size.x),
            self.position.y + self.half_size.y - (collided_actor.position.y - collided_actor.half_size.y),
            collided_actor.position.y + collided_actor.half_size.y - (self.position.y - self.half_size.y)
        )

