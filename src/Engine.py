from Renderer import Renderer

import pygame



class Engine:
    def __init__(self, game):
        pygame.init()
        self.actors_to_draw = {}
        self.renderer = Renderer(game.window_width, game.window_height, game.window_title)

        self.running = True


    def register_actor(self, actor, b_render = True):
        if b_render:
            if actor.name in self.actors_to_draw:
                raise Exception(f"Actor {actor.name} is already registered")
            self.actors_to_draw[actor.name] = actor


    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


    def render(self):
        for actor in self.actors_to_draw.values():
            self.renderer.add_actor_to_draw(actor)

        self.renderer.render()
        self.renderer.clear()

        if not self.running:
            pygame.quit()
