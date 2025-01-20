from Game import Game
from Plane import Plane
from Datatypes import *



def main():
    game = Game()

    plane = Plane("Plane", 2**.5/2, "res/textures/texture.jpeg")

    game.renderer.add_actor_to_draw(plane)

    game.renderer.camera.position = Vector(0, 0, 1)
    game.renderer.camera.rotation = Rotator(math.radians(-90), 0, 0)

    while game.running:
        game.tick()
        game.render()



if __name__ == "__main__":
    main()

    