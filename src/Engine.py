from Renderer import Renderer

import pygame



class Engine(Renderer):
    def __init__(self, game):
        self.fps = game.fps_cap

        pygame.init()
        self.__actors = {}
        super().__init__(game.window_width, game.window_height, game.camera_width, game.window_title)

        self.running = True
        self.__clock = pygame.time.Clock()


    @property
    def fps(self):
        return self.__fps
    

    @fps.setter
    def fps(self, value):
        if isinstance(value, int) and value > 0:
            self.__fps = value
        else:
            raise Exception("FPS must be a positive integer:", value)


    @property
    def running(self):
        return self.__running
    

    @running.setter
    def running(self, value):
        if isinstance(value, bool):
            self.__running = value
        else:
            raise Exception("Running must be a boolean:", value)


    @property
    def actors(self):
        return self.__actors
    

    @property
    def clock(self):
        return self.__clock


    def register_actor(self, actor, b_render = True):
        if b_render:
            if actor.name in self.actors_to_draw:
                raise Exception(f"Actor {actor.name} is already registered")
            self.__actors[actor.name] = actor


    def tick(self):
        self.clear()
        delta_time = self.clock.tick(self.fps) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        if not self.running:
            pygame.quit()
            return

        for actor in self.actors.values():
            actor.tick(delta_time)
            if actor.visible:
                self.add_actor_to_draw(actor)

        self.render()

        return delta_time

