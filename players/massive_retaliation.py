from .utils import player_wrapper

@player_wrapper
def massive_retaliation(last_opponent_action=None):
    if last_opponent_action == 0:
        return 0
    else:
        return 1
