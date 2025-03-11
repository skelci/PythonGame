from enginet.engine import *

from componentst.datatypes import *



#?ifdef CLIENT
class ClientGameBase:
    def __init__(self):
        self.__engine = ClientEngine()
    

    @property
    def engine(self):
        return self.__engine


    def tick(self):
        return self.engine.tick() 

#?endif



#?ifdef SERVER
class ServerGameBase:
    def __init__(self):
        self.__engine = ServerEngine()
    

    @property
    def engine(self):
        return self.__engine


    def tick(self):
        return self.engine.tick()

#?endif

