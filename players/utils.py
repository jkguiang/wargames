from . import PLAYERS

def player_wrapper(func):
    global PLAYERS
    PLAYERS[func.__name__] = func
    def player(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return player
