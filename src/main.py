from game.game import *



#?ifdef CLIENT
def client_main():
    client_game = ClientGame()

    while client_game.engine.running:
        client_game.tick()

#?endif



#?ifdef SERVER
def server_main():
    server_game = ServerGame()

    while server_game.engine.running:
        server_game.tick()

#?endif



if __name__ == "__main__":
    #?ifdef CLIENT
    client_main()
    #?endif

    #?ifdef SERVER
    server_main()
    #?endif

