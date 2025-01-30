from Engine import Engine



class GameBase:
    def __init__(self):
        self.window_title = "Game"
        self.window_width = 800
        self.window_height = 600
        self.running = False


    def begin_play(self):
        self.engine = Engine(self)
        self.running = True


    def tick(self):
        self.engine.tick()
        self.engine.render()
