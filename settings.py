from enum import IntEnum

MAX_DISTANCE_BETWEEN_POINTS = 50

class GameState(IntEnum):
    MAIN_MENU = 1
    IN_GAME = 2
    GAME_OVER = 3
    ABOUT = 4