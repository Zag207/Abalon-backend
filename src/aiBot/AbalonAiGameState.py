from typing import Tuple

import numpy as np
import numpy.typing as npt

from aiBot.action_space import ActionSpace
from base_alpha_zero.Game import Game


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
        board = 2 * np.ones((n, n), dtype=np.int8)

        # Кол-во валидных клеток в строках гекса
        row_lens = [5, 6, 7, 8, 9, 8, 7, 6, 5]

        for r, ln in enumerate(row_lens):
            start = (n - ln) // 2
            board[r, start:start + ln] = 0

        # Классическая стартовая расстановка (14 на 14)
        # Верх (белые)
        board[0, 2:7] = 1          # 5
        board[1, 1:7] = 1          # 6
        board[2, 3:6] = 1          # 3

        # Низ (чёрные)
        board[8, 2:7] = -1           # 5
        board[7, 1:7] = -1           # 6
        board[6, 3:6] = -1           # 3

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

            
