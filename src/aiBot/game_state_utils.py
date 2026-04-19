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

def get_matrix_from_board(board: GameState) -> npt.NDArray[np.int8]:
        # Коды:
        #  1  - белая фишка
        # -1  - черная фишка
        #  0  - пустая валидная клетка
        #  2  - несуществующая (вне гекса), если храните доску как 9x9
        n = 9
        board_matrix = 0 * np.ones((n, n), dtype=np.int8)

        offset = 4
        for i in range(0, 4):
            board_matrix[:offset, i] = 2
            offset -= 1
        
        offset = 1
        for i in range(5, 9):
            board_matrix[(9 - offset):, i] = 2
            offset += 1


        for circle in fill_circle_board():
            coords = circle.coords
            circle_team = circle.circle_type

            board_matrix[coords.line - 1, coords.diagonal - 1] = get_team_code(circle_team)

        return board_matrix

def get_circles_by_coords(board: Board, circle_coords: List[CircleCoords]) -> List[Circle]:
    return [circle for circle in board.circles if circle.coords in circle_coords]
