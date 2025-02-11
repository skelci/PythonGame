from game import Game



def main():
    game = Game()

    game.begin_play()

    while game.engine.running:
        game.tick()

    game.end_play()



if __name__ == "__main__":
    main()

