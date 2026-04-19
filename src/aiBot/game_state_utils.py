from typing import List
from ctypes import ArgumentError

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam

import numpy.typing as npt
import numpy as np

from core.game_state import GameState
from core.geometry.circle_coords import CircleCoords
from core.setup.prepare_circles import fill_circle_board


def get_team_code(circle_team: CircleTeam) -> int:
    match circle_team:
        case CircleTeam.White:
            return 1
        case CircleTeam.Black:
            return -1

def get_team_from_code(circle_team_code: int) -> CircleTeam:
    match circle_team_code:
        case 1:
            return CircleTeam.White
        case -1:
            return CircleTeam.Black
        case _:
            raise ArgumentError("Unknown team code")

def get_board_from_matrix_board(matrix_board: npt.NDArray[np.int8]) -> Board:
    linesW, diagonalsW = np.where(matrix_board == 1)
    linesB, diagonalsB = np.where(matrix_board == -1)

    circles = [Circle(CircleCoords(line + 1, diagonal + 1), CircleTeam.White) for line, diagonal in zip(linesW, diagonalsW)]
    circles.extend([Circle(CircleCoords(line + 1, diagonal + 1), CircleTeam.Black) for line, diagonal in zip(linesB, diagonalsB)])

    return Board(circles)

def get_circles_by_coords(board: Board, circle_coords: List[CircleCoords]) -> List[Circle]:
    return [circle for circle in board.circles if circle.coords in circle_coords]
