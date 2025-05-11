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
    def key_C(engine_ref, level_ref, id):
        # Spawn Entities at the player's position
        coal_entity = Coal("coal_entity", Vector(-5, 26))
        gold_entity = RawGoldNugget("gold_entity", Vector(-4, 26))
        iron_entity = RawIronNugget("iron_entity", Vector(-3, 26))
        stone_entity = Rock("stone_entity", Vector(-2, 26))
        dirt_entity = DirtPile("dirt_entity", Vector(-1, 26))
        log_entity = Wood("log_entity", Vector(-6, 26))
        stick_entity = Stick("stick_entity", Vector(-7, 26))
        leaf_entity = Leaf("leaf_entity", Vector(-8, 26))
        diamond_entity = Diamond("diamond_entity", Vector(-9, 26))
        sand_entity = SandPile("sand_entity", Vector(-10, 26))

        level_ref.register_actor(coal_entity)
        level_ref.register_actor(gold_entity)
        level_ref.register_actor(iron_entity)
        level_ref.register_actor(stone_entity)
        level_ref.register_actor(dirt_entity)
        level_ref.register_actor(log_entity)
        level_ref.register_actor(stick_entity)
        level_ref.register_actor(leaf_entity)
        level_ref.register_actor(diamond_entity)
        level_ref.register_actor(sand_entity)


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
        self.engine.register_key(Keys.MOUSE_LEFT, KeyPressType.HOLD, KeyHandler.destroy_blocks)

        #?ifdef ENGINE
        self.engine.console.handle_cmd("build_server")
        self.engine.console.handle_cmd("build_client")
        #?endif

        for x in range(-2, 3):
            for y in range(-2, 3):
                self.world_generator.generate_and_load_chunks(Vector(x, y))

        self.engine.start_network("0.0.0.0", 5555, 10)
            

    def tick(self):
        delta_time = super().tick()

        for player in self.engine.players.values():
            divider = self.world_generator.chunk_size / CHUNK_SIZE
            ud = player.update_distance // divider + 3
            ud = int(clamp(ud, 1, 8))
            chk = get_chunk_cords(player.position) // divider

            for offset_y in range(-ud, ud):
                for offset_x in range(-ud, ud):
                    self.world_generator.generate_and_load_chunks(chk + (offset_x, offset_y))




