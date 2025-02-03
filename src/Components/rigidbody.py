from components.actor import Actor

from components.datatypes import *



class Rigidbody(Actor):
    def __init__(self, name, half_size, position = Vector(), visible = False, texture = None, restitution = 0.5, initial_velocity = Vector(), min_velocity = 0, mass = 1):
        super().__init__(name, half_size, position, visible, texture, restitution)

        self.velocity = initial_velocity
        self.min_velocity = min_velocity
        self.mass = mass
        

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
    def min_velocity(self):
        return self.__min_velocity
    

    @min_velocity.setter
    def min_velocity(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__min_velocity = value
        else:
            raise Exception("Min velocity must be a positive float:", value)
        

    @property
    def mass(self):
        return self.__mass
    

    @mass.setter
    def mass(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__mass = value
        else:
            raise Exception("Mass must be a positive float:", value)
        

    def on_collision(self, collision_data):
        # Bounce based on formula: j = v_rel * -(1 + e) / (1 / m1 + 1 / m2)
        v_rel = self.velocity - collision_data.velocity
        e = self.restitution * collision_data.restitution
        j = v_rel * -(1 + e) / (1 / self.mass + 1 / collision_data.mass)
        self.velocity += j / self.mass


    def tick(self, delta_time):
        if self.velocity.length < self.min_velocity:
            self.velocity = Vector(0, 0)


    def is_colliding(self, collided_actor):
        distances = self.__get_edge_distances(collided_actor)
        return (
            all(d > 0 for d in distances),
            distances
        )


    def collision_response_direction(self, collided_actor):
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
            direction.y = -push_down
        else:
            direction.y = push_up
        
        return direction
        

    def __get_edge_distances(self, collided_actor):
        # right, left, top, bottom
        return (
            self.position.x + self.half_size.x - (collided_actor.position.x - collided_actor.half_size.x),
            collided_actor.position.x + collided_actor.half_size.x - (self.position.x - self.half_size.x),
            self.position.y + self.half_size.y - (collided_actor.position.y - collided_actor.half_size.y),
            collided_actor.position.y + collided_actor.half_size.y - (self.position.y - self.half_size.y)
        )
    
    