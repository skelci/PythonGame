from Renderer import Renderer

import pygame



class Game:
    def __init__(self):
        self.running = True

        pygame.init()
        self.renderer = Renderer(1200, 800, "3D Engine")


    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def render(self):
        self.renderer.render()

        if not self.running:
            pygame.quit()
