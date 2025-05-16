#?attr SERVER

from engine.core.game_base import ServerGameBase

from engine.components.level import Level
from engine.game_math import *

from .blocks import *
from .world_generation.world_generation import WorldGeneration



class Overworld(Level):
    def __init__(self):
        super().__init__("Overworld", Player, [], "sky")



class KeyHandler:
    @staticmethod
    def key_W(engine_ref, level_ref, id, delta_time):
        level_ref.actors[engine_ref.get_player_actor(id)].jump()


    @staticmethod
    def key_A(engine_ref, level_ref, id, delta_time):
        level_ref.actors[engine_ref.get_player_actor(id)].move_direction = -1


    @staticmethod
    def key_D(engine_ref, level_ref, id, delta_time):
        level_ref.actors[engine_ref.get_player_actor(id)].move_direction = 1

    @staticmethod
    def scroll_up(engine_ref, level_ref, id):
        player = level_ref.actors[engine_ref.get_player_actor(id)]
        player.set_inventory_slot((player.current_inventory_slot - 1) % 10)
    
    @staticmethod
    def scroll_down(engine_ref, level_ref, id):
        player = level_ref.actors[engine_ref.get_player_actor(id)]
        player.set_inventory_slot((player.current_inventory_slot + 1) % 10)
    
    @staticmethod
    def slot_selection(engine_ref, level_ref, id, slot):
        player = level_ref.actors[engine_ref.get_player_actor(id)]
        player.set_inventory_slot(slot)
    

    @staticmethod
    def place_block(engine_ref, level_ref, id):
        mouse_pos = engine_ref.players[id].world_mouse_pos
        player_actor = level_ref.actors[engine_ref.get_player_actor(id)]
        if mouse_pos.distance_to(player_actor.position) > 3:
            return
        item_to_place = player_actor.inventory_list[player_actor.current_inventory_slot]
        if not item_to_place:
            return
        match item_to_place:
            case "Furnace":
                block = Furnace(f"furnace_{mouse_pos}_{time.time()}", mouse_pos.rounded + 0.5)
                player_actor.remove_from_inventory(item_to_place)
            case "Anvil":
                block = Anvil(f"anvil_{mouse_pos}_{time.time()}", mouse_pos.rounded + 0.5)
                player_actor.remove_from_inventory(item_to_place)
                
            case _:
                return
        level_ref.register_actor(block)
    

    @staticmethod
    def use_block(engine_ref, level_ref, id):
        player_pos = level_ref.actors[engine_ref.get_player_actor(id)].position
        actors = level_ref.get_actors_in_chunk(get_chunk_cords(player_pos))

        for actor in actors:
            if isinstance(actor, Furnace) and player_pos.distance_to(actor.position) < 1:
                print("open furnace")
                return
            elif isinstance(actor, Anvil) and player_pos.distance_to(actor.position) < 1:
                print("open anvil")
                return
        

    @staticmethod
    def key_C(engine_ref, level_ref, id):
        coal = Coal("coal", Vector(-5, 26))
        gold = RawGoldNugget("gold", Vector(-4, 26))
        iron = RawIronNugget("iron", Vector(-3, 26))
        stone = Rock("stone", Vector(-2, 26))
        dirt = DirtPile("dirt", Vector(-1, 26))
        log = Wood("log", Vector(-6, 26))
        stick = Stick("stick", Vector(-7, 26))
        leaf = Leaf("leaf", Vector(-8, 26))
        diamond = Diamond("diamond", Vector(-9, 26))
        sand = SandPile("sand", Vector(-10, 26))
        seed = Seed("seed", Vector(-11, 26))

        level_ref.register_actor(coal)
        level_ref.register_actor(gold)
        level_ref.register_actor(iron)
        level_ref.register_actor(stone)
        level_ref.register_actor(dirt)
        level_ref.register_actor(log)
        level_ref.register_actor(stick)
        level_ref.register_actor(leaf)
        level_ref.register_actor(diamond)
        level_ref.register_actor(sand)
        level_ref.register_actor(seed)


    def destroy_blocks(engine_ref, level_ref, id, delta_time):
        player_pos = level_ref.actors[engine_ref.get_player_actor(id)].position
        mouse_pos = engine_ref.players[id].world_mouse_pos

        acotrs = level_ref.get_actors_in_chunks_3x3(get_chunk_cords(player_pos))

        breaking_blocks = []

        for actor in acotrs:
            bl_pos = actor.position - actor.half_size
            tr_pos = actor.position + actor.half_size

            if is_in_rect(bl_pos, tr_pos, mouse_pos) and isinstance(actor, WorldBlock):
                breaking_blocks.append(actor)

        if not breaking_blocks:
            return

        top_block = sorted(breaking_blocks, key=lambda x: x.render_layer)[-1]
        top_block.punch(delta_time)



class ServerGame(ServerGameBase):
    def __init__(self):
        super().__init__()
        self.engine.max_tps = 120
        
        self.engine.register_level(Overworld())

        seed = random.randint(0, 9999)
        
        self.world_generator = WorldGeneration(self.engine.levels["Overworld"], seed)
        
        self.current_base_chunk = Vector(0, 0)

        self.engine.register_key(Keys.W, KeyPressType.HOLD, KeyHandler.key_W)
        self.engine.register_key(Keys.A, KeyPressType.HOLD, KeyHandler.key_A)
        self.engine.register_key(Keys.D, KeyPressType.HOLD, KeyHandler.key_D)
        self.engine.register_key(Keys.C, KeyPressType.TRIGGER, KeyHandler.key_C)
        self.engine.register_key(Keys.MOUSE_SCROLL_UP, KeyPressType.TRIGGER, KeyHandler.scroll_up)
        self.engine.register_key(Keys.MOUSE_SCROLL_DOWN, KeyPressType.TRIGGER, KeyHandler.scroll_down)
        self.engine.register_key(Keys.MOUSE_LEFT, KeyPressType.HOLD, KeyHandler.destroy_blocks)
        self.engine.register_key(Keys.MOUSE_RIGHT, KeyPressType.RELEASE, KeyHandler.place_block)
        self.engine.register_key(Keys.E, KeyPressType.TRIGGER, KeyHandler.use_block)
        self.engine.register_key(Keys.KEY_1, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 0))
        self.engine.register_key(Keys.KEY_2, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 1))
        self.engine.register_key(Keys.KEY_3, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 2))
        self.engine.register_key(Keys.KEY_4, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 3))
        self.engine.register_key(Keys.KEY_5, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 4))
        self.engine.register_key(Keys.KEY_6, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 5))
        self.engine.register_key(Keys.KEY_7, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 6))
        self.engine.register_key(Keys.KEY_8, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 7))
        self.engine.register_key(Keys.KEY_9, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 8))
        self.engine.register_key(Keys.KEY_0, KeyPressType.TRIGGER, lambda e, l, id: KeyHandler.slot_selection(e, l, id, 9))

        for x in range(-2, 3):
            for y in range(-2, 3):
                self.world_generator.generate_and_load_chunks(Vector(x, y))

        self.engine.start_network("0.0.0.0", 5555, 10)
            

    def tick(self):
        delta_time = super().tick()

        for id, player in self.engine.players.items():
            divider = self.world_generator.chunk_size / CHUNK_SIZE
            ud = player.update_distance // divider + 3
            ud = int(clamp(ud, 1, 8))
            chk = get_chunk_cords(player.position) // divider

            for offset_y in range(-ud, ud):
                for offset_x in range(-ud, ud):
                    self.world_generator.generate_and_load_chunks(chk + (offset_x, offset_y))

            if not player.level:
                continue
            player_actor = self.engine.levels[player.level].actors.get(self.engine.get_player_actor(id))
            if not player_actor:
                continue
            player_actor.set_hunger(-delta_time * 0.1)