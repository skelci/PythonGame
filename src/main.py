from game.game import *

#?ifdef ENGINE
import threading
#?endif



#?ifdef ENGINE
def tick_server():
    server_game = ServerGame()
    while server_game.engine.running:
        server_game.tick()


def engine_main():
    server_thread = threading.Thread(target=tick_server)
    server_thread.daemon = True
    server_thread.start()

    client_game = ClientGame()
    while client_game.engine.running:
        client_game.tick()

    exit()

#?endif



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
    #?ifdef ENGINE
    engine_main()
    #?endif

    #?ifdef CLIENT
    client_main()
    #?endif

    #?ifdef SERVER
    server_main()
    #?endif

