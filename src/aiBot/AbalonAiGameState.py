from typing import Tuple

import numpy as np
import numpy.typing as npt

from base_alpha_zero.Game import Game


class AbalonAiGameState(Game):
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
