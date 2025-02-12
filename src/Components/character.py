from components.rigidbody import Rigidbody

from components.datatypes import *



class Character(Rigidbody):
    def __init__(self, name, half_size, position = Vector(), visible = True, material = None, restitution = 0.01, initial_velocity = Vector(), min_velocity = kinda_small_number, mass = 100, gravity_scale = 1, friction = 8, air_resistance = 0.1, jump_velocity = 7, walk_speed = 500, acceleration = 800, air_control = 0.2):
        super().__init__(name, half_size, position, visible, material, restitution, initial_velocity, min_velocity, mass, gravity_scale, friction, air_resistance)
        
        self.jump_velocity = jump_velocity
        self.walk_speed = walk_speed
        self.acceleration = acceleration
        self.air_control = air_control


    @property
    def jump_velocity(self):
        return self.__jump_velocity
    

    @jump_velocity.setter
    def jump_velocity(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__jump_velocity = value
        else:
            raise Exception("Jump velocity must be a positive float:", value)
        

    @property
    def walk_speed(self):
        return self.__walk_speed
    

    @walk_speed.setter
    def walk_speed(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__walk_speed = value
        else:
            raise Exception("Walk speed must be a positive float:", value)
        

    @property
    def acceleration(self):
        return self.__acceleration
    

    @acceleration.setter
    def acceleration(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__acceleration = value
        else:
            raise Exception("Acceleration must be a positive float:", value)
        

    @property
    def air_control(self):
        return self.__air_control
    

    @air_control.setter
    def air_control(self, value):
        if isinstance(value, (int, float)) and value >= 0:
            self.__air_control = value
        else:
            raise Exception("Air control must be a positive float:", value)
        

    @property
    def is_grounded(self):
        return self.collided_sides.y > 0
        

    def move(self, direction, delta_time):
        print("velocity:", self.velocity)
        if self.velocity.abs.x < self.walk_speed:
            if self.is_grounded:
                self.velocity.x += direction * self.acceleration * delta_time
                if self.velocity.abs.x > self.walk_speed:
                    self.velocity.x = direction * self.walk_speed
            else:
                self.velocity.x += direction * self.acceleration * self.air_control * delta_time
                if self.velocity.abs.x > self.walk_speed * self.air_control:
                    self.velocity.x = direction * self.walk_speed * self.air_control

        if direction > 0:
            self.material.mirror = False
        elif direction < 0:
            self.material.mirror = True


    def jump(self):
        if self.is_grounded:
            self.velocity.y = self.jump_velocity
            

