
from typing import List, Tuple

import numpy as np
import numpy.typing as npt

from core.geometry.circle_coords import CircleCoords
from core.geometry.delta_coords import DeltaCoords
from core.movement.moving_types import MovingTypes

from ..game_state_utils import get_team_code, get_team_from_code
from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.movement.moving_directions import MovingDirections

# Не работать с голыми кодами, а с перечислениями

def _is_in_numpy_board(coords, board: npt.NDArray[np.int8]) -> bool:
    return Board.is_in_board(coords) and 0 <= coords.line - 1 < board.shape[0] and 0 <= coords.diagonal - 1 < board.shape[1]

def is_circles_exist(circles_checked: List[Circle], board: npt.NDArray[np.int8]) -> bool:
    return all(
        board[circle.coords.line - 1, circle.coords.diagonal - 1] == get_team_code(circle.circle_type) 
        for circle in circles_checked
        )

def check_for_parall_move(circles_checked: List[Circle], board: npt.NDArray[np.int8], player_code: int, action_direction: MovingDirections) -> bool:
    # Не уверен, что работает корректно, нужно тестировать
    
    if len(circles_checked) == 0:
        return False

    coords_set = {(circle.coords.line, circle.coords.diagonal) for circle in circles_checked}
    if len(coords_set) != len(circles_checked):
        return False

    if not all(_is_in_numpy_board(circle.coords, board) for circle in circles_checked):
        return False

    lines = [circle.coords.line for circle in circles_checked]
    diagonals = [circle.coords.diagonal for circle in circles_checked]

    is_one_line = all(circle.coords.line == lines[0] for circle in circles_checked)
    is_one_diagonal = all(circle.coords.diagonal == diagonals[0] for circle in circles_checked)

    sorted_circles_checked = sorted(circles_checked, key=lambda c: c.coords.diagonal)

    is_one_other_diagonal = True
    for i in range(1, len(sorted_circles_checked)):
        line_dist = sorted_circles_checked[i].coords.line - sorted_circles_checked[i - 1].coords.line
        diagonal_dist = sorted_circles_checked[i].coords.diagonal - sorted_circles_checked[i - 1].coords.diagonal
        status = (-1 <= line_dist <= 0) and (diagonal_dist == 1 or diagonal_dist == 0)
        if not status:
            is_one_other_diagonal = False
            break

    is_move_valid = is_one_line or is_one_diagonal or is_one_other_diagonal
    if not is_move_valid:
        return False

    delta_coords = DeltaCoords.get_delta_coords_from_moving(action_direction)
    if not all(
        _is_in_numpy_board(circle.coords.get_new_coords(delta_coords), board)
        and board[circle.coords.get_new_coords(delta_coords).line - 1, circle.coords.get_new_coords(delta_coords).diagonal - 1] == 0
        for circle in circles_checked
    ):
        return False

    sorted_circles_checked = sorted(circles_checked, key=lambda c: c.coords.get_distance(circles_checked[0].coords))
    if not all(
        sorted_circles_checked[i].coords.get_distance(sorted_circles_checked[i + 1].coords) <= 1
        for i in range(len(sorted_circles_checked) - 1)
    ):
        return False

    return True

def get_circle_line(
        circle_checked: Circle, 
        board: npt.NDArray[np.int8], 
        action_direction: MovingDirections
        ) -> Tuple[List[Circle], CircleCoords | None]:
    if circle_checked is None:
        return [], None

    delta_coords = DeltaCoords.get_delta_coords_from_moving(action_direction)

    circle_line: List[Circle] = [circle_checked]
    next_coords = circle_line[-1].coords.get_new_coords(delta_coords)

    while _is_in_numpy_board(next_coords, board) and board[next_coords.line - 1, next_coords.diagonal - 1] not in [0, 2]:
        circle_type_code = board[next_coords.line - 1, next_coords.diagonal - 1]
        circle_type = get_team_from_code(circle_type_code)
        circle_line.append(
            Circle(next_coords, circle_type)
        )
        next_coords = circle_line[-1].coords.get_new_coords(delta_coords)
    return circle_line, next_coords

def check_for_linear_move(circle_checked: Circle, board: npt.NDArray[np.int8], player_code: int, action_direction: MovingDirections) -> bool:
    # Не уверен, что работает корректно, нужно тестировать
    
    circle_line, next_coords = get_circle_line(circle_checked, board, action_direction)
    delta_coords = DeltaCoords.get_delta_coords_from_moving(action_direction)

    if len(circle_line) == 0:
        return False

    my_team_circle_count = sum(1 for circle in circle_line if board[circle.coords.line - 1, circle.coords.diagonal - 1] == player_code)
    enemy_circle_count = len(circle_line) - my_team_circle_count

    if my_team_circle_count > 3:
        return False

    last_my_circle = next(
        (circle for circle in reversed(circle_line) if board[circle.coords.line - 1, circle.coords.diagonal - 1] == player_code),
        None
    )
    if last_my_circle is None:
        return False

    is_end_board = next_coords is not None and not Board.is_in_board(next_coords)

    if enemy_circle_count > 0:
        if enemy_circle_count >= my_team_circle_count:
            return False

        first_enemy_circle = next(
            (circle for circle in circle_line if board[circle.coords.line - 1, circle.coords.diagonal - 1] != player_code),
            None
        )
        if first_enemy_circle is None:
            return False

        expected_enemy_coords = last_my_circle.coords.get_new_coords(delta_coords)
        if (
            first_enemy_circle.coords.line != expected_enemy_coords.line
            or first_enemy_circle.coords.diagonal != expected_enemy_coords.diagonal
        ):
            return False
    elif is_end_board:
        return False

    return True

def validate_action(
        circles_checked: list[Circle], 
        board: npt.NDArray[np.int8], 
        player: CircleTeam,
        action_direction: MovingDirections
        ) -> bool:
    moving_type = Board.get_moving_type(len(circles_checked))
    player_code = get_team_code(player)

    is_move_valid = len(circles_checked) > 0
    is_move_valid = is_move_valid and is_circles_exist(circles_checked, board)

    if not is_move_valid:
        return is_move_valid
    
    match moving_type:
        case MovingTypes.Parall:
            is_move_valid = check_for_parall_move(
                circles_checked, 
                board, 
                player_code, 
                action_direction
                )
        case MovingTypes.Linear:
            is_move_valid = check_for_linear_move(
                circles_checked[0], 
                board, 
                player_code, 
                action_direction
                )
    
    return is_move_valid
    

