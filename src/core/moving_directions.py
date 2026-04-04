from enum import Enum


class MovingDirections(Enum):
    NoMove = 0
    UpRight = 1
    Right = 2
    DownRight = 3
    DownLeft = 4
    Left = 5
    UpLeft = 6