from components.datatypes import *
from components.material import Material


class Actor:
    def __init__(self, engine_ref, name, half_size, position = Vector(), generate_overlap_events = False, collidable = True, visible = True, material = None, restitution = 1):
        self.__outdated = {
            "half_size": False,
            "position": False,
            "visible": False,
            "material": False,
        }

        self.engine_ref = engine_ref
        self.name = name
        self.half_size = half_size
        self.position = position
        self.generate_overlap_events = generate_overlap_events
        self.collidable = collidable
        self.visible = visible
        self.material = material
        self.restitution = restitution

        self.previously_collided = set()

        for k, v in self.__outdated.items():
            if v:
                self.__outdated[k] = False



    @property
    def engine_ref(self):
        return self.__engine_ref
    

    @engine_ref.setter
    def engine_ref(self, value):
        if value.__class__.__name__ == "ServerEngine" or value.__class__.__name__ == "ClientEngine":
            self.__engine_ref = value
        else:
            raise TypeError("Engine refrence must be a Engine object:", value)


    @property
    def name(self):
        return self.__name
    

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
        else:
            raise TypeError("Name must be a string:", value)


    @property
    def half_size(self):
        return self.__half_size
    

    @half_size.setter
    def half_size(self, value):
        if isinstance(value, Vector) and value.x > 0 and value.y > 0:
            self.__half_size = value
            self.__outdated["half_size"] = True
        else:
            raise TypeError("Half size must be a Vector:", value)
        

    @property
    def position(self):
        return self.__position
    

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self.__position = value
            self.__outdated["position"] = True
        else:
            raise TypeError("Position must be a Vector:", value)
        

    @property
    def generate_overlap_events(self):
        return self.__generate_overlap_events
    

    @generate_overlap_events.setter
    def generate_overlap_events(self, value):
        if isinstance(value, bool):
            self.__generate_overlap_events = value
        else:
            raise TypeError("Generate overlap events must be a bool:", value)
        

    @property
    def collidable(self):
        return self.__collidable
    

    @collidable.setter
    def collidable(self, value):
        if isinstance(value, bool):
            self.__collidable = value
        else:
            raise TypeError("Simulate physics must be a bool:", value)
        

    @property
    def visible(self):
        return self.__visible
    

    @visible.setter
    def visible(self, value):
        if isinstance(value, bool):
            self.__visible = value
            self.__outdated["visible"] = True
        else:
            raise TypeError("Visible must be a bool:", value)
        

    @property
    def material(self):
        return self.__material
    

    @material.setter
    def material(self, value):
        if issubclass(value.__class__, Material) or value == None:
            self.__material = value
            self.__outdated["material"] = True
        else:
            raise TypeError("Material name must be a string None:", value)
        

    @property
    def restitution(self):
        return self.__restitution
    

    @restitution.setter
    def restitution(self, value):
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            self.__restitution = value
        else:
            raise TypeError("Restitution must be a float between 0 and 1:", value)
        

    @property
    def previously_collided(self):
        return self.__previously_collided
    

    @previously_collided.setter
    def previously_collided(self, value):
        if isinstance(value, set):
            self.__previously_collided = value
        else:
            raise TypeError("Previously collided must be a set:", value)
        

    #?ifdef CLIENT
    def update_from_net_sync(self, data):
        for key in data:
            match key:
                case "half_size":
                    self.half_size = Vector(*data[key])
                case "position":
                    self.position = Vector(*data[key])
                case "visible":
                    self.visible = data[key]
                case "material":
                    self.material = self.engine_ref.get_material(data[key])
        

    #?ifdef SERVER
    def get_for_full_net_sync(self):
        for key in self.__outdated:
            self.__outdated[key] = False
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "half_size": self.half_size,
            "position": self.position,
            "visible": self.visible,
            "material": self.material.texture_str if self.material else None
        }
    

    def get_for_net_sync(self):
        out = {}
        for key in self.__outdated:
            if self.__outdated[key]:
                if key == "material":
                    out[key] = self.material.name if self.material else None
                out[key] = getattr(self, key)
                self.__outdated[key] = False

        return out


    def tick(self, delta_time):
        pass


    def on_collision(self, collision_data):
        pass


    def on_overlap_begin(self, other_actor):
        pass


    def on_overlap_end(self, other_actor):
        pass
    #?endif

    
    def __str__(self):
        return self.name


