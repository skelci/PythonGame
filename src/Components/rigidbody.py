from components.actor import Actor

from components.datatypes import *



class Rigidbody(Actor):
    def __init__(self, name, half_size, position = Vector(), visible = True, texture = None, initial_velocity = Vector(), restitution = 0.5, min_velocity = Vector(0.01, 0.01)):
        super().__init__(name, half_size, position, visible, texture)

        self.velocity = initial_velocity
        self.restitution = restitution
        self.min_velocity = min_velocity
        

    @property
    def velocity(self):
        return self.__velocity
    

    @velocity.setter
    def velocity(self, value):
        if isinstance(value, Vector):
            self.__velocity = value
        else:
            raise Exception("Velocity must be a Vector:", value)
        

    @property
    def restitution(self):
        return self.__restitution
    

    @restitution.setter
    def restitution(self, value):
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            self.__restitution = value
        else:
            raise Exception("Restitution must be a float between 0 and 1:", value)
        

    @property
    def min_velocity(self):
        return self.__min_velocity
    

    @min_velocity.setter
    def min_velocity(self, value):
        if isinstance(value, Vector) and value.abs == value:
            self.__min_velocity = value
        elif isinstance(value, (int, float)):
            self.__min_velocity = Vector(value, value)
        else:
            raise Exception("Min velocity must be a positive Vector or a positive float:", value)
        

    def on_collision(self, collided_direction):
        self.velocity = -collided_direction.abs * self.velocity * self.restitution


    def tick(self, delta_time):
        if self.velocity.lenght < self.min_velocity.lenght:
            self.velocity = Vector(0, 0)


    def is_colliding(self, other_actor):
        distances = self.__get_edge_distances(other_actor)
        return (
            all(d > 0 for d in distances),
            distances
        )


    def collision_response_direction(self, other_actor):
        is_colliding, distances = self.is_colliding(other_actor)
        if not is_colliding:
            return Vector(0, 0)  # No collision → no push

        # Distances needed to push out
        push_right, push_left, push_up, push_down = distances
        
        # Pick the smallest push
        min_push = min(push_right, push_left, push_down, push_up)
        
        # Determine direction based on which push is smallest
        direction = Vector(0, 0)
        if min_push == push_right:
            direction.x = -push_right
        elif min_push == push_left:
            direction.x = push_left
        elif min_push == push_down:
            direction.y = -push_down
        else:
            direction.y = push_up
        
        # Return the vector to move out of collision
        return direction
        

    def __get_edge_distances(self, other_actor):
        # right, left, top, bottom
        return (
            self.position.x + self.half_size.x - (other_actor.position.x - other_actor.half_size.x),
            other_actor.position.x + other_actor.half_size.x - (self.position.x - self.half_size.x),
            self.position.y + self.half_size.y - (other_actor.position.y - other_actor.half_size.y),
            other_actor.position.y + other_actor.half_size.y - (self.position.y - self.half_size.y)
        )
    
    