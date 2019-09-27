from .utils import player_wrapper

@player_wrapper
def tit_for_tat(last_opponent_action=None):
    if last_opponent_action:
        return last_opponent_action
    else:
        return 1
