"""
Template classes for the game.
Template code in game/game.py:
```
from engine.game_base import *
class ClientGame(ClientGameBase):
    pass
class ServerGame(ServerGameBase):
    pass
```
"""

from engine.engine import *

from components.datatypes import *



#?ifdef CLIENT
class ClientGameBase:
    def __init__(self):
        """ Initializes the client engine. """
        self.__engine = ClientEngine()
    

    @property
    def engine(self):
        """ ClientEngine - The engine instance for the client. """
        return self.__engine


    def tick(self):
        """
        Ticks the engine.
        Returns:
            float - delta_time. The time elapsed since the last tick.
        """
        return self.engine.tick() 

#?endif



#?ifdef SERVER
class ServerGameBase:
    def __init__(self):
        """ Initializes the server engine. """
        self.__engine = ServerEngine()
    

    @property
    def engine(self):
        """ ServerEngine - The engine instance for the server. """
        return self.__engine


    def tick(self):
        """
        Ticks the engine.
        Returns:
            float - delta time. The time elapsed since the last tick.
        """
        return self.engine.tick()

#?endif

