from engine.datatypes import *
from engine.components.actors.actor import Actor
from engine.components.actors.character import Character
from engine.components.actors.rigidbody import Rigidbody
from engine.components.material import Material

import random


#   JURE


class Log(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5),collidable=False, material = Material("res/textures/log.png"))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        
        count=random.randint(3,5)
        LogName = f"log_{self.name}"
        LogEntity_ = LogEntity(LogName, self.position, count=count)
        self.level_ref.register_actor(LogEntity_)
        self.engine_ref.play_sound("res/sounds/log_destroyed.mp3", self.level_ref.name, self.position, 8, 2)
        #print('wood iz log')

class Leaf(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), collidable=False, material = Material("res/textures/leaf_block.png"), render_layer=1)
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        
        count=random.randint(0,5)
        StickName = f"stick_{self.name}"
        StickEntity_ = StickEntity(StickName, self.position, count=count)
        self.level_ref.register_actor(StickEntity_)
        #print("stick iz leaf") 

        LeafName = f"leaf_{self.name}"
        LeafEntity_ = LeafEntity(LeafName, self.position, count=8)
        self.level_ref.register_actor(LeafEntity_)
        #print("leaves:", j) 

class Grass(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/grass_block.png"))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        count=4
        GrassDirtName = f"grass_dirt_{self.name}"
        GrassDirtEntity= DirtEntity(GrassDirtName, self.position, count=count)
        self.level_ref.register_actor(GrassDirtEntity)
        #print("entity dirt iz grasa")
        self.engine_ref.play_sound("res/sounds/grass_destroyed.mp3", self.level_ref.name, self.position, 8, 1)

class Sand(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material(Color(255, 255, 0)))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        count=2
        SandName = f"sand_{self.name}"
        SandEntity= SandEntity(SandName, self.position, count=count)
        self.level_ref.register_actor(SandEntity)
        #print("entity sand iz sanda")
        #self.engine_ref.play_sound("res/sounds/dirt_destroyed.mp3", self.level_ref.name, self.position, 8, 1)

class Dirt(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/dirt.png"))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        
        count=random.randint(3,5)
        DirtName = f"dirt_{self.name}"
        dirt_entity = DirtEntity(DirtName, self.position, count=count)
        self.level_ref.register_actor(dirt_entity)
        self.engine_ref.play_sound("res/sounds/dirt_destroyed.mp3", self.level_ref.name, self.position, 8, 1)
        
        #print('dirt iz dirta')

        chance=random.randint(1,4)
        if chance==1:
            self.level_ref.register_actor(StoneEntity(f"stone_{self.name}", self.position))
            #print('stone iz dirta') 
 
class Stone(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/stone.png"))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        count=random.randint(3,5)
        StoneName = f"stone_{self.name}"
        stone_entity = StoneEntity(StoneName, self.position, count=count)
        self.level_ref.register_actor(stone_entity)
        self.engine_ref.play_sound("res/sounds/stone_destroyed.mp3", self.level_ref.name, self.position, 8, 1)
        #print('rock iz stone')     

class Coal(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/coal_ore.png"))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        
        spawn_extra_stones = random.randint(1, 2)
        stone_count = 3 if spawn_extra_stones == 1 else 2

        self.level_ref.register_actor(CoalEntity(self.name, self.position))  
        RockCoalName = f"rock_coal_{self.name}"
        RockCoalEntity = StoneEntity(RockCoalName, self.position, count=stone_count)
        self.level_ref.register_actor(RockCoalEntity)
        self.engine_ref.play_sound("res/sounds/stone_destroyed.mp3", self.level_ref.name, self.position, 8, 1)
        #print("rock iz coala")  

class Iron(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/iron_ore.png"))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        
        IronName = f"iron_{self.name}"
        IronEnntity = IronEntity(IronName, self.position, count=3)
        self.level_ref.register_actor(IronEnntity) 

        spawn_extra_stones = random.randint(1, 2)
        stone_count = 3 if spawn_extra_stones == 1 else 2

        RockIronName = f"rock_iron_{self.name}"
        RockIronEntity = StoneEntity(RockIronName, self.position, count=stone_count)
        self.level_ref.register_actor(RockIronEntity)
        self.engine_ref.play_sound("res/sounds/stone_destroyed.mp3", self.level_ref.name, self.position, 8, 1)
        #print("rock iz irona")   

class Gold(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material("res/textures/gold_ore.png"))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        
        GoldName = f"gold_{self.name}"
        Gold_Entity = GoldEntity(GoldName, self.position, count=3)
        self.level_ref.register_actor(Gold_Entity) 

        spawn_extra_stones = random.randint(1, 2)
        stone_count = 3 if spawn_extra_stones == 1 else 2

        RockGoldName = f"rock_gold_{self.name}"
        RockGoldEntity = StoneEntity(RockGoldName, self.position, count=stone_count)
        self.level_ref.register_actor(RockGoldEntity)
        self.engine_ref.play_sound("res/sounds/stone_destroyed.mp3", self.level_ref.name, self.position, 8, 1)
        #print("rock iz golda")

class Diamond(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(0.5, 0.5), material = Material(Color(0, 0, 255)))
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        
        DiamondName = f"diamond_{self.name}"
        DiamondEntity = DiamondEntity(DiamondName, self.position, count=1)
        self.level_ref.register_actor(DiamondEntity) 

        spawn_extra_stones = random.randint(1, 2)
        stone_count = 3 if spawn_extra_stones == 1 else 2

        RockDiamondName = f"rock_diamond_{self.name}"
        RockDiamondEntity = StoneEntity(RockDiamondName, self.position, count=stone_count)
        self.level_ref.register_actor(RockDiamondEntity)
        self.engine_ref.play_sound("res/sounds/stone_destroyed.mp3", self.level_ref.name, self.position, 8, 1)
    
class Furnace(Actor):
    def __init__(self, name, position):
        super().__init__(name, position = position, half_size = Vector(1, 1), material = Material(0, 0, 0), collidable=False)
        self.position = position
    def on_destroyed(self):
        if self.engine_ref.__class__.__name__ == "ClientEngine":
            return
        count = 4
        StoneName = f"stone_{self.name}"
        stone_entity = StoneEntity(StoneName, self.position, count=count)
        self.level_ref.register_actor(stone_entity)
        self.engine_ref.play_sound("res/sounds/stone_destroyed.mp3", self.level_ref.name, self.position, 8, 1)


class DebugTunnel(Actor):
    def __init__(self, name, position):
        super().__init__(name, position=position, half_size=Vector(0.5, 0.5), collidable=False, material=Material(Color(255, 0, 0)), render_layer=1)  # Bright red
        self.position = position

class TestPlayer(Character):
    def __init__(self, name, position):
        super().__init__(name, position=Vector(-5, 25), material = Material(Color(0, 0, 255)), jump_velocity=7, render_layer=2, initial_velocity=Vector())
        self.inventory = {}
   
        

    def add_to_inventory(self, item_name, count=0):
        #print("adding to inventory")
        if item_name in self.inventory:
            self.inventory[item_name] += count
        else:
            self.inventory[item_name] = count
        self.engine_ref.network.send(self.id, "update_inventory", self.inventory, True)

        # Display the inventory for debugging purposes
        #print(f"Inventory: {self.inventory}")

def pick_me_up(self, other_actor):
        #print("pick me up")
        if isinstance(other_actor, Character):
            self.engine_ref.play_sound("res/sounds/pick_up.mp3", self.level_ref.name, self.position, 4, 0.5)
            other_actor.add_to_inventory(self.__class__.__name__, self.count)
            self.level_ref.destroy_actor(self)


class LogEntity(Rigidbody):
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y) 
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/log_entity.png"), restitution=0, initial_velocity=Initial_velocity)   
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)


class StickEntity(Rigidbody):    
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/stick_entity.png"), restitution=0, initial_velocity=Initial_velocity)           
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class DirtEntity(Rigidbody):        
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        #print(self.count)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/dirt_entity.png"), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class SandEntity(Rigidbody):
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        #print(self.count)
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material(Color(255, 255, 0)), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)


class GrassEntity(Rigidbody):        
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material(Color(255, 0, 0)), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class StoneEntity(Rigidbody):    
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/stone_entity.png"), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class CoalEntity(Rigidbody):    
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/coal_ore_entity.png"), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class IronEntity(Rigidbody):    
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/iron_ore_entity.png"), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class GoldEntity(Rigidbody):    
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/gold_ore_entity.png"), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class DiamondEntity(Rigidbody):    
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material(Color(0, 0, 255)), restitution=0, initial_velocity=Initial_velocity)
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class FurnaceEntity(Rigidbody):
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material(Color(0, 0, 0)), restitution=0, initial_velocity=Initial_velocity)                       
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

class LeafEntity(Rigidbody):
    def __init__(self, name, position, count=1):
        angle = random.uniform(0,2*math.pi)
        velocity_x = math.cos(angle) 
        velocity_y = math.sin(angle)
        Initial_velocity = Vector(velocity_x, velocity_y)
        self.count = count
        super().__init__(name, position=position, half_size=Vector(0.25, 0.25), collidable=False, material=Material("res/textures/leaf_entity.png"), restitution=0, initial_velocity=Initial_velocity)                       
    def on_overlap_begin(self, other_actor):
        pick_me_up(self, other_actor)

