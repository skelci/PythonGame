from game import Game



def main():
    game = Game()

    game.begin_play()

    while game.engine.running:
        game.tick()



if __name__ == "__main__":
    main()

