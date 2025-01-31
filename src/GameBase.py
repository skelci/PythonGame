from Engine import Engine



class GameBase:
    def __init__(self):
        self.window_title = "Game"
        self.window_width = 800
        self.window_height = 600
        self.camera_width = 10


    @property
    def window_title(self):
        return self.__window_title
    

    @window_title.setter
    def window_title(self, value):
        if isinstance(value, str):
            self.__window_title = value
        else:
            raise Exception("Window title must be a string:", value)
        

    @property
    def window_width(self):
        return self.__window_width
    

    @window_width.setter
    def window_width(self, value):
        if isinstance(value, int) and value > 0:
            self.__window_width = value
        else:
            raise Exception("Window width must be a positive integer:", value)
        

    @property
    def window_height(self):
        return self.__window_height
    

    @window_height.setter
    def window_height(self, value):
        if isinstance(value, int) and value > 0:
            self.__window_height = value
        else:
            raise Exception("Window height must be a positive integer:", value)
        

    @property
    def camera_width(self):
        return self.__camera_width
    

    @camera_width.setter
    def camera_width(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__camera_width = value
        else:
            raise Exception("Camera width must be a positive integer:", value)
        

    @property
    def engine(self):
        return self.__engine


    def begin_play(self):
        self.__engine = Engine(self)


    def tick(self):
        self.engine.tick()
