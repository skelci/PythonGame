"""
This module provides a logging utility for the game engine.
"""

import time
from enum import IntEnum



class LogType(IntEnum):
    """Enumeration for different log types."""
    INFO = 1
    WARNING = 2
    ERROR = 3
    DEBUG = 4



def log(message: str, log_type: LogType = LogType.DEBUG):
    """
    Logs a message with a specific log type.
    Args:
        message (str): The message to log.
        log_type (LogType): The type of log (INFO, WARNING, ERROR, DEBUG).
    """

    RESET = "\033[0m"
    COLORS = {
        LogType.INFO: "\033[94m",    # Blue
        LogType.WARNING: "\033[93m", # Yellow
        LogType.ERROR: "\033[91m",   # Red
        LogType.DEBUG: "\033[92m"    # Green
    }

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    color = COLORS[log_type]
    formatted = f"[{timestamp}] [{log_type.name}] {message}"
    print(f"{color}{formatted}{RESET}")



#?ifdef CLIENT
def log_client(message: str, log_type: LogType = LogType.DEBUG):
    """
    Logs a message for the client with a specific log type.
    Args:
        message (str): The message to log.
        log_type (LogType): The type of log (INFO, WARNING, ERROR, DEBUG).
    """
    #?ifdef ENGINE
    log(f"[CLIENT] {message}", log_type)
    return
    #?endif
    log(message, log_type)
#?endif



#?ifdef SERVER
def log_server(message: str, log_type: LogType = LogType.DEBUG):
    """
    Logs a message for the server with a specific log type.
    Args:
        message (str): The message to log.
        log_type (LogType): The type of log (INFO, WARNING, ERROR, DEBUG).
    """
    #?ifdef ENGINE
    log(f"[SERVER] {message}", log_type)
    return
    #?endif
    log(message, log_type)
#?endif



#?ifdef ENGINE
def log_engine(message: str, log_type: LogType = LogType.DEBUG):
    """
    Logs a message for the engine with a specific log type.
    Args:
        message (str): The message to log.
        log_type (LogType): The type of log (INFO, WARNING, ERROR, DEBUG).
    """
    log(f"[ENGINE] {message}", log_type)
#?endif


