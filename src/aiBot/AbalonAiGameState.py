from dataclasses import dataclass
import logging
from typing import Tuple

import numpy as np
import numpy.typing as npt

from action_space import ActionSpace
from base_alpha_zero.Game import Game
from game_state_utils import get_team_code, get_team_from_code
from network_utils import board_to_three_masks
from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.game_state import GameState
from core.movement.moving_directions import MovingDirections
from core.setup.prepare_circles import fill_circle_board

log = logging.getLogger(__name__)

file_handler = logging.FileHandler('app2.log')
log.addHandler(file_handler)

class AbalonAiGameState(Game):
    action_space: ActionSpace

    def __init__(self):
        super().__init__()

        self.action_space = ActionSpace()
        self._direction_by_delta = {
            MovingDirections.get_moving_vector(direction): direction
            for direction in MovingDirections
            if direction != MovingDirections.NoMove
        }
        self._action_index_by_signature = {
            self._action_signature(action.selected_coords, action.direction): idx
            for idx, action in enumerate(self.action_space.action_space)
        }

    @staticmethod
    def _axial_from_coords(coords: CircleCoords) -> tuple[int, int]:
        # Center of the hex in current coordinates is (5, 5).
        return coords.line - 5, coords.diagonal - 5

    @staticmethod
    def _coords_from_axial(q: int, r: int) -> CircleCoords:
        return CircleCoords(q + 5, r + 5)

    @staticmethod
    def _transform_axial(q: int, r: int, rotation: int, reflect: bool) -> tuple[int, int]:
        if reflect:
            q, r = r, q

        for _ in range(rotation % 6):
            q, r = -r, q + r

        return q, r

    def _transform_coords(self, coords: CircleCoords, rotation: int, reflect: bool) -> CircleCoords:
        q, r = self._axial_from_coords(coords)
        q_t, r_t = self._transform_axial(q, r, rotation, reflect)
        return self._coords_from_axial(q_t, r_t)

    def _transform_direction(self, direction: MovingDirections, rotation: int, reflect: bool) -> MovingDirections:
        dq, dr = MovingDirections.get_moving_vector(direction)
        dq_t, dr_t = self._transform_axial(dq, dr, rotation, reflect)
        mapped = self._direction_by_delta.get((dq_t, dr_t))

        if mapped is None:
            raise ValueError(f"Unknown transformed direction delta: {(dq_t, dr_t)}")

        return mapped

    @staticmethod
    def _action_signature(selected_coords: list[CircleCoords], direction: MovingDirections) -> tuple[tuple[tuple[int, int], ...], MovingDirections]:
        coords_key = tuple(sorted((coords.line, coords.diagonal) for coords in selected_coords))
        return coords_key, direction

    def _transform_action(self, action_index: int, rotation: int, reflect: bool) -> int:
        action = self.action_space[action_index]
        if action is None:
            raise IndexError(f"Invalid action index: {action_index}")

        transformed_coords = [
            self._transform_coords(coords, rotation, reflect)
            for coords in action.selected_coords
        ]
        transformed_direction = self._transform_direction(action.direction, rotation, reflect)
        signature = self._action_signature(transformed_coords, transformed_direction)

        mapped_index = self._action_index_by_signature.get(signature)
        if mapped_index is None:
            raise KeyError(f"No mapped action found for signature: {signature}")

        return mapped_index

    def _transform_state(self, board: GameState, rotation: int, reflect: bool) -> GameState:
        transformed_circles = [
            Circle(self._transform_coords(circle.coords, rotation, reflect), circle.circle_type)
            for circle in board.board.circles
        ]

        transformed_state = GameState(transformed_circles)
        transformed_state.curr_team = board.curr_team
        transformed_state.score_white = board.score_white
        transformed_state.score_black = board.score_black
        transformed_state.move_count = board.move_count
        transformed_state.last_score_change_move = board.last_score_change_move
        return transformed_state

    def getInitBoard(self):
        # Коды:
        #  1  - белая фишка
        # -1  - черная фишка
        #  0  - пустая валидная клетка
        #  2  - несуществующая (вне гекса), если храните доску как 9x9
        # n = 9
        # board = 0 * np.ones((n, n), dtype=np.int8)

        # offset = 4
        # for i in range(0, 4):
        #     board[:offset, i] = 2
        #     offset -= 1
        
        # offset = 1
        # for i in range(5, 9):
        #     board[(9 - offset):, i] = 2
        #     offset += 1


        # for circle in fill_circle_board():
        #     coords = circle.coords
        #     circle_team = circle.circle_type

        #     board[coords.line - 1, coords.diagonal - 1] = get_team_code(circle_team)

        # return board

        return GameState(fill_circle_board())
    
    def getBoardSize(self) -> Tuple[int, int]:
        return (9, 9)
    
    def getActionSize(self) -> int:
        return self.action_space.actions_count
    
    def getGameEnded(self, board: GameState, player: int) -> float | None:
        """
        Возвращает value (награду) для текущего игрока если игра закончилась.
        
        Возвращает:
        - None: если игра еще не закончилась
        - 1.0: если текущий игрок выиграл традиционным способом (6 очков)
        - -1.0: если текущий игрок проиграл традиционным способом
        - 0.8: если текущий игрок выиграл по количеству очков при лимите ходов
        - -0.8: если текущий игрок проиграл по количеству очков при лимите ходов
        - 0.0: если ничья при лимите ходов (одинаковое количество очков)
        """
        curr_team = get_team_from_code(player)
        return board.get_value_for_player(curr_team)
    
    def getCanonicalForm(self, board: GameState, player: int) -> GameState:
        curr_team = get_team_from_code(player)
        board_new = board.clone()

        if curr_team == CircleTeam.White:
            return board_new

        for circle in board_new.board.circles:
            if circle.circle_type == CircleTeam.White:
                circle.circle_type = CircleTeam.Black
            else:
                circle.circle_type = CircleTeam.White

        return board_new
    
    def getValidMoves(self, board: GameState, player: int) -> npt.NDArray[np.int8]:
        valid_moves_mask = 0*np.ones(self.getActionSize(), dtype=np.int8)
        curr_team = get_team_from_code(player)

        # Не эффективно, можно оптимизировать, если проверять валидные ходы от текущего состояния доски, а не проверять весь пул
        # Но тогда бы пришлось придумывать, как их одназначно кодировать для нейросети

        for index, action in enumerate(self.action_space.action_space):
            action_coords = action.selected_coords
            circles = [Circle(coords, curr_team) for coords in action_coords]
            is_action_valid, _ = board.board.get_move_validation_result(
                circles,
                action.direction,
                curr_team,
                Board.get_moving_type(len(circles))
                )
            valid_moves_mask[index] = is_action_valid

        
        return valid_moves_mask
    
    def getNextState(self, board: GameState, player: int, action: int) -> Tuple[GameState, int]:
        curr_player = get_team_from_code(player)

        new_state = board.clone()
        
        action_obj = self.action_space[action]

        if action_obj is None:
            raise AttributeError("action_obj is None")
        
        # Сохраняем старые очки для проверки изменения
        old_score_black = new_state.score_black
        old_score_white = new_state.score_white
        old_move_count = new_state.move_count
        
        circles_checked = [Circle(coords, curr_player) for coords in action_obj.selected_coords]
        move_direction = action_obj.direction

        new_state.board.move(circles_checked, move_direction, curr_player)
        
        # Увеличиваем счетчик ходов при переходе в новое состояние
        new_state.move_count += 1
        
        # Если счет изменился, обновляем last_score_change_move
        if new_state.score_black > old_score_black or new_state.score_white > old_score_white:
            new_state.last_score_change_move = new_state.move_count
            log.debug(f"Счет изменился! Ход {new_state.move_count}: Черные={new_state.score_black}, Белые={new_state.score_white}")

        return new_state, -player

    def getSymmetries(self, board: GameState, pi) -> list[tuple[GameState, npt.NDArray[np.float32]]]:
        pi_array = np.asarray(pi, dtype=np.float32)
        if pi_array.shape[0] != self.getActionSize():
            raise ValueError(
                f"pi size mismatch: expected {self.getActionSize()}, got {pi_array.shape[0]}"
            )

        # symmetries: list[tuple[GameState, npt.NDArray[np.float32]]] = []
        # operations = [(rotation, False) for rotation in range(6)] + [(rotation, True) for rotation in range(6)]

        # for rotation, reflect in operations:
        #     transformed_state = self._transform_state(board, rotation, reflect)
        #     transformed_pi = np.zeros(self.getActionSize(), dtype=np.float32)

        #     for action_index, prob in enumerate(pi_array):
        #         if prob == 0:
        #             continue

        #         mapped_index = self._transform_action(action_index, rotation, reflect)
        #         transformed_pi[mapped_index] += prob

        #     symmetries.append((transformed_state, transformed_pi))

        # return symmetries

        return [(board, pi_array)]


    def to_matrix(self, board: GameState) -> npt.NDArray[np.int8]:
        matrix = np.zeros((9, 9), dtype=np.int8)

        # Mark forbidden hexes (outside the hex grid)
        offset = 4
        for i in range(0, 4):
            matrix[:offset, i] = 2
            offset -= 1
        
        offset = 1
        for i in range(5, 9):
            matrix[(9 - offset):, i] = 2
            offset += 1

        # Place circles from the given board state
        for circle in board.board.circles:
            coords = circle.coords
            circle_team = circle.circle_type
            matrix[coords.line - 1, coords.diagonal - 1] = get_team_code(circle_team)

        return matrix

    def toNetworkInput(self, board: GameState) -> npt.NDArray[np.float32]:
        matrix = self.to_matrix(board)

        return board_to_three_masks(matrix)

    def stringRepresentation(self, board: GameState) -> str:
        circles_repr = sorted(
            (
                circle.coords.line,
                circle.coords.diagonal,
                1 if circle.circle_type == CircleTeam.White else -1,
            )
            for circle in board.board.circles
        )

        curr_team_code = 1 if board.curr_team == CircleTeam.White else -1
        state_header = f"turn:{curr_team_code}|sw:{board.score_white}|sb:{board.score_black}"
        circles_state = "|".join(f"{line},{diagonal},{team}" for line, diagonal, team in circles_repr)

        return f"{state_header}|{circles_state}"
            
