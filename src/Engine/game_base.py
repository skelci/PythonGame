from engine.engine import Engine

from components.datatypes import *



class GameBase:
    @property
    def engine(self):
        return self.__engine


    def begin_play(self):
        self.__engine = Engine()


    def tick(self):
        return self.engine.tick() 
    

    def end_play(self):
        pass
