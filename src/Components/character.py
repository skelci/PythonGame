from components.rigidbody import Rigidbody

from components.datatypes import *



class Character(Rigidbody):
    def __init__(self, game_refrence, name, half_size, position = Vector(), visible = True, material = None, restitution = 0, initial_velocity = Vector(), min_velocity = kinda_small_number, mass = 100, gravity_scale = 1, friction = 8, air_resistance = 0.1, jump_velocity = 7, walk_speed = 5, acceleration = 10, air_control = 0.2):
        super().__init__(game_refrence, name, half_size, position, visible, material, restitution, initial_velocity, min_velocity, mass, gravity_scale, friction, air_resistance)
        
        self.jump_velocity = jump_velocity
        self.walk_speed = walk_speed
        self.acceleration = acceleration
        self.air_control = air_control
        self.move_direction = 0


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
    def move_direction(self):
        return self.__move_direction
    

    @move_direction.setter
    def move_direction(self, value):
        if isinstance(value, int) and value in [-1, 0, 1]:
            self.__move_direction = value
        else:
            raise Exception("Move direction must be -1, 0 or 1:", value)


    @property
    def is_grounded(self):
        return self.collided_sides[3] != 0
        

    def jump(self):
        if self.is_grounded:
            self.velocity.y = self.jump_velocity


    def __move(self, delta_time):
        direction = self.move_direction
        dad = direction * self.acceleration * delta_time
        if self.velocity.abs.x < self.walk_speed:
            if self.is_grounded:
                self.velocity.x += dad
                if self.velocity.abs.x > self.walk_speed:
                    self.velocity.x -= self.walk_speed * self.friction * dad
                    if self.velocity.abs.x < self.walk_speed:
                        self.velocity.x = direction * self.walk_speed
            else:
                wa = self.walk_speed * self.air_control
                self.velocity.x += self.air_control * dad
                if self.velocity.abs.x > wa:
                    self.velocity.x -= wa * self.air_resistance * dad
                    if self.velocity.abs.x < wa:
                        self.velocity.x = direction * wa


        if direction > 0:
            self.material.mirror = False
        elif direction < 0:
            self.material.mirror = True


    def tick(self, delta_time):
        # Min velocity
        if self.velocity.abs.x < self.min_velocity:
            self.velocity.x = 0
        if self.velocity.abs.y < self.min_velocity:
            self.velocity.y = 0

        # Gravity
        if self.collided_sides[3] == 0:
            self.velocity.y += gravity * self.gravity_scale * delta_time

        # Air resistance
        v_change = self.velocity * self.air_resistance * delta_time
        if self.velocity.length < v_change.length:
            self.velocity = Vector(0, 0)
        else:
            self.velocity -= v_change
        
        # Friction
        if self.is_grounded and self.move_direction == 0:
            v_change = self.velocity.x * self.friction * delta_time
            if self.velocity.abs.x < abs(v_change):
                self.velocity.x = 0
            else:
                self.velocity -= v_change

        self.__move(delta_time)


        
            

