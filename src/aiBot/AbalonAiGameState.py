from typing import Tuple

import numpy as np
import numpy.typing as npt

from aiBot.action_space import ActionSpace
from aiBot.base_alpha_zero.Game import Game
from aiBot.game_state_utils import get_team_code
from core.setup.prepare_circles import fill_circle_board

#TODO: Сделать автоперевод игровой доски в формат alpha-zero - массив numpy

class AbalonAiGameState(Game):
    action_space: ActionSpace

    def __init__(self):
        super().__init__()

        self.action_space = ActionSpace()

    def getInitBoard(self) -> npt.NDArray[np.integer]:
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
    
    def getGameEnded(self, board: npt.NDArray[np.integer], player: int) -> int:
        is_white_won = (14 - np.count_nonzero(board == 1)) >= 6
        is_black_won = (14 - np.count_nonzero(board == -1)) >= 6

        if (is_white_won and player == 1) or \
            (is_black_won and player == -1):
            return 1
        elif is_white_won or is_black_won == 0:
            return 0
        else:
            return -1
    
    def getCanonicalForm(self, board: npt.NDArray[np.integer], player: int) -> npt.NDArray[np.integer]:
        if player == -1:
            new_board = np.where(board == -1, 20, board)
            new_board[new_board == 1] = -1
            new_board[new_board == 20] = 1
            return new_board

        return board.copy() 

            
