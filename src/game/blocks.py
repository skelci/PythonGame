from engine.datatypes import *
from engine.components.actors.actor import Actor
from engine.components.actors.character import Character
from engine.components.actors.rigidbody import Rigidbody
from engine.components.material import Material

import random
import time
from abc import ABC, abstractmethod



def register_actor_templates(engine_ref):
    eng = engine_ref
    eng.register_actor_template(Player)
    eng.register_actor_template(Log)
    eng.register_actor_template(LeafBlock)
    eng.register_actor_template(GrassBlock)
    eng.register_actor_template(Grass)
    eng.register_actor_template(Seed)
    eng.register_actor_template(Sand)
    eng.register_actor_template(Dirt)
    eng.register_actor_template(Stone)
    eng.register_actor_template(CoalOre)
    eng.register_actor_template(IronOre)
    eng.register_actor_template(GoldOre)
    eng.register_actor_template(DiamondOre)
    eng.register_actor_template(Furnace)
    eng.register_actor_template(SandPile)
    eng.register_actor_template(DirtPile)
    eng.register_actor_template(Wood)
    eng.register_actor_template(Stick)
    eng.register_actor_template(Rock)
    eng.register_actor_template(Coal)
    eng.register_actor_template(RawIronNugget)
    eng.register_actor_template(RawGoldNugget)
    eng.register_actor_template(Leaf)
    eng.register_actor_template(Diamond)



class Player(Character):
    def __init__(self, name, position):
        super().__init__(name, position=Vector(-5, 28), material = Material("res/textures/player.png"), jump_velocity=7, render_layer=5, initial_velocity=Vector())
        self.inventory_dict = {"Furnace": 1}
        self.inventory_list = [None] * 10
        self.inventory_list[8] = "Furnace"
        self.current_inventory_slot = 0
        self.health = 100
        self.hunger = 100
        

    def add_to_inventory(self, item_name, count):
        if len(self.inventory_dict) >= 10 and item_name not in self.inventory_dict:
            return False
        
        if item_name in self.inventory_dict:
            self.inventory_dict[item_name] += count
        else:
            self.inventory_dict[item_name] = count
            for i in range(10):
                if self.inventory_list[i] is None:
                    self.inventory_list[i] = item_name
                    break
        self.engine_ref.network.send(self.id, "update_inventory", (self.inventory_dict, self.inventory_list))
        return True


    def remove_from_inventory(self, item_name, count = 1):
        if item_name not in self.inventory_dict:
            return False
        
        self.inventory_dict[item_name] -= count
        if self.inventory_dict[item_name] <= 0:
            del self.inventory_dict[item_name]
            for i in range(10):
                if self.inventory_list[i] == item_name:
                    self.inventory_list[i] = None
                    break
        self.engine_ref.network.send(self.id, "update_inventory", (self.inventory_dict, self.inventory_list))
        return True
    

    def set_inventory_slot(self, slot):
        if slot < 0 or slot >= len(self.inventory_list):
            return
        self.current_inventory_slot = slot
        self.engine_ref.network.send(self.id, "set_inventory_slot", slot)


    def on_collision(self, collision_data):
        if self.velocity.y < -10:
            self.health -= abs(self.velocity.y)
            self.engine_ref.network.send(self.id, "health", self.health)
        super().on_collision(collision_data)

    def set_hunger(self, hunger):
        self.hunger += hunger
        self.engine_ref.network.send(self.id, "hunger", self.hunger)




class WorldBlock(Actor, ABC):
    def __init__(self, name, position, hardness, material, collidable=True, render_layer=0):
        super().__init__(name, position, collidable=collidable, material=Material(f"res/textures/{material}"), render_layer=render_layer)
        self.hardness = hardness
        self.durability = hardness
        

    def punch(self, damage):
        self.durability -= damage
        if self.durability <= 0:
            self.on_destroyed()


    @abstractmethod
    def on_destroyed(self, dropped_items, sound):
        """
        dropped_items should look like this:
        { item_class: tuple(min_count, max_count) }
        """
        self.engine_ref.play_sound(f"res/sounds/block_destroyed/{sound}", self.level_ref.name, self.position, 8, 1)
        self.level_ref.destroy_actor(self)
        
        for item_class, (min_count, max_count) in dropped_items.items():
            count = random.uniform(min_count, max_count).__int__()
            if count <= 0:
                continue

            item_name = f"{item_class.__name__}{self.position}{time.time():.2f}"
            item = item_class(item_name, self.position)
            
            item.count = count
            self.level_ref.register_actor(item)



class Log(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "log.png", False)

    def on_destroyed(self):
        super().on_destroyed({Wood: (3, 5)}, "log_destroyed.mp3")


class LeafBlock(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 1, "leaf_block.png", False, render_layer=3)

    def on_destroyed(self):
        super().on_destroyed({Leaf: (0, 5), Stick: (0, 5)}, "grass_destroyed.mp3")


class GrassBlock(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "grass_block.png")

    def on_destroyed(self):
        super().on_destroyed({DirtPile: (4, 5)}, "grass_destroyed.mp3")

class Grass(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 0.5, "grass.png", False, render_layer=15)

    def on_destroyed(self):
        super().on_destroyed({Seed: (4, 5)}, "grass_destroyed.mp3")


class Sand(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "sand.png")

    def on_destroyed(self):
        super().on_destroyed({SandPile: (3, 6)}, "sand_destroyed.mp3")


class Dirt(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "dirt.png")

    def on_destroyed(self):
        super().on_destroyed({DirtPile: (3, 5), Rock: (0.5, 1)}, "dirt_destroyed.mp3")


class Stone(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "stone.png")

    def on_destroyed(self):
        super().on_destroyed({Rock: (3, 5)}, "stone_destroyed.mp3")


class CoalOre(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "coal_ore.png")

    def on_destroyed(self):
        super().on_destroyed({Coal: (1, 3), Rock: (2, 4)}, "stone_destroyed.mp3")


class IronOre(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "iron_ore.png")

    def on_destroyed(self):
        super().on_destroyed({RawIronNugget: (1, 3), Rock: (2, 4)}, "stone_destroyed.mp3")


class GoldOre(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "gold_ore.png")

    def on_destroyed(self):
        super().on_destroyed({RawGoldNugget: (1, 3), Rock: (2, 4)}, "stone_destroyed.mp3")


class DiamondOre(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "diamond_ore.png")

    def on_destroyed(self):
        super().on_destroyed({Diamond: (1, 3), Rock: (2, 4)}, "stone_destroyed.mp3")


class Furnace(WorldBlock):
    def __init__(self, name, position):
        super().__init__(name, position, 2, "furnace.png", False, render_layer=1)
        self.half_size = Vector(1, 1)

    def on_destroyed(self):
        super().on_destroyed({Rock: (6, 10)}, "stone_destroyed.mp3")



class Entity(Rigidbody, ABC):
    def __init__(self, name, position, material):
        alpha = random.uniform(0, PI)
        velocity = Vector(math.cos(alpha), math.sin(alpha))
        super().__init__(name, position, Vector(0.25, 0.25), collidable=False, material=Material(f"res/textures/{material}"), render_layer=10, restitution=0, initial_velocity=velocity)
        self.count = 1


    def on_overlap_begin(self, other_actor):
        if not isinstance(other_actor, Player):
            return
        if not other_actor.add_to_inventory(self.__class__.__name__, self.count):
            return
        
        self.engine_ref.play_sound("res/sounds/pick_up.mp3", self.level_ref.name, self.position, 4, 0.5)
        self.level_ref.destroy_actor(self)
    


class Wood(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "wood.png")


class Leaf(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "leaf.png")


class Stick(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "stick.png")

class Seed(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "seed.png")

class DirtPile(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "dirt_pile.png")


class SandPile(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "sand_pile.png")


class Rock(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "rock.png")


class Coal(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "coal.png")


class RawIronNugget(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "iron_nugget.png")


class RawGoldNugget(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "gold_nugget.png")


class Diamond(Entity):
    def __init__(self, name, position):
        super().__init__(name, position, "diamond.png")

