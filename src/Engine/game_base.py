from engine.engine import Engine

from components.datatypes import *



class GameBase:
    def __init__(self):
        self.window_title = "Game"
        self.window_width = 800
        self.window_height = 600
        self.camera_width = 10
        self.fps_cap = 60
        self.min_tps = 50
        self.fullscreen = False
        self.windowed = False
        self.camera_position = Vector()


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
    def fps_cap(self):
        return self.__fps_cap
    

    @fps_cap.setter
    def fps_cap(self, value):
        if isinstance(value, int) and value > 0:
            self.__fps_cap = value
        else:
            raise Exception("FPS cap must be a positive integer:", value)
        

    @property
    def min_tps(self):
        return self.__min_tps
    

    @min_tps.setter
    def min_tps(self, value):
        if isinstance(value, (int, float)) and value > 0:
            self.__min_tps = value
        else:
            raise Exception("Minimum TPS must be a positive number:", value)
        

    @property
    def fullscreen(self):
        return self.__fullscreen
    

    @fullscreen.setter
    def fullscreen(self, value):
        if isinstance(value, bool):
            self.__fullscreen = value
        else:
            raise Exception("Fullscreen must be a bool:", value)
        

    @property
    def windowed(self):
        return self.__windowed
    

    @windowed.setter
    def windowed(self, value):
        if isinstance(value, bool):
            self.__windowed = value
        else:
            raise Exception("Windowed must be a bool:", value)
        

    @property
    def camera_position(self):
        return self.__camera_position
    

    @camera_position.setter
    def camera_position(self, value):
        if isinstance(value, Vector):
            self.__camera_position = value
        else:
            raise Exception("Camera position must be a Vector:", value)


    @property
    def engine(self):
        return self.__engine


    def begin_play(self):
        self.__engine = Engine(self)


    def tick(self):
        delta_time = self.engine.tick()
        return delta_time
