from typing import Tuple

import numpy as np
from numpy._typing import NDArray
import numpy.typing as npt

from aiBot.action_space import ActionSpace
from aiBot.base_alpha_zero.Game import Game
from aiBot.game_state_utils import get_board_from_matrix_board, get_team_code, get_team_from_code
from core.board.board import Board
from core.board.circle import Circle
from core.setup.prepare_circles import fill_circle_board

#TODO: Сделать автоперевод игровой доски в формат alpha-zero - массив numpy

class AbalonAiGameState(Game):
    action_space: ActionSpace

    def __init__(self):
        super().__init__()

        self.action_space = ActionSpace()

    def getInitBoard(self) -> npt.NDArray[np.int8]:
        # Коды:
        #  1  - белая фишка
        # -1  - черная фишка
        #  0  - пустая валидная клетка
        #  2  - несуществующая (вне гекса), если храните доску как 9x9
        n = 9
        board = 0 * np.ones((n, n), dtype=np.int8)

        offset = 4
        for i in range(0, 4):
            board[:offset, i] = 2
            offset -= 1
        
        offset = 1
        for i in range(5, 9):
            board[(9 - offset):, i] = 2
            offset += 1


        for circle in fill_circle_board():
            coords = circle.coords
            circle_team = circle.circle_type

            board[coords.line - 1, coords.diagonal - 1] = get_team_code(circle_team)

        return board
    
    def getBoardSize(self) -> Tuple[int, int]:
        return (14, 14)
    
    def getActionSize(self) -> int:
        return self.action_space.actions_count
    
    def getGameEnded(self, board: npt.NDArray[np.int8], player: int) -> int:
        is_white_won = (14 - np.count_nonzero(board == 1)) >= 6
        is_black_won = (14 - np.count_nonzero(board == -1)) >= 6

        if (is_white_won and player == 1) or \
            (is_black_won and player == -1):
            return 1
        elif is_white_won or is_black_won == 0:
            return 0
        else:
            return -1
    
    def getCanonicalForm(self, board: npt.NDArray[np.int8], player: int) -> npt.NDArray[np.int8]:
        if player == -1:
            new_board = np.where(board == -1, 20, board)
            new_board[new_board == 1] = -1
            new_board[new_board == 20] = 1
            return new_board

        return board.copy()
    
    def getValidMoves(self, board: npt.NDArray[np.int8], player: int) -> npt.NDArray[np.int8]:
        valid_moves_mask = 0*np.ones(self.getActionSize(), dtype=np.int8)
        board_new = get_board_from_matrix_board(board)
        curr_team = get_team_from_code(player)

        # Не эффективно, можно оптимизировать, если проверять валидные ходы от текущего состояния доски, а не проверять весь пул
        # Но тогда бы пришлось придумывать, как их одназначно кодировать для нейросети

        for index, action in enumerate(self.action_space.action_space):
            action_coords = action.selected_coords
            circles = [Circle(coords, curr_team) for coords in action_coords]
            is_action_valid, _ = board_new.get_move_validation_result(
                circles,
                action.direction,
                curr_team,
                Board.get_moving_type(len(circles))
                )
            valid_moves_mask[index] = is_action_valid

        
        return valid_moves_mask
    
    def stringRepresentation(self, board: npt.NDArray) -> str:
        return str(board)
            
