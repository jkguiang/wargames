import glob

PLAYERS = {}
MODULE_DIR = __file__.split("__init__")[0]
MODULE_NAME = MODULE_DIR.split("/")[-2]

excepts = [__file__, MODULE_DIR+"utils.py"]
paths = list(set(glob.glob(MODULE_DIR+"*.py"))-set(excepts))
for path_to_player in paths:
    player = (path_to_player.split("/")[-1]).split(".py")[0]
    __import__(MODULE_NAME+"."+player)
