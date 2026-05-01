from dataclasses import dataclass

import numpy as np


@dataclass
class NumpyAbalonGameState:
    board: np.ndarray  # 9x9 matrix representation of the board
    score_black: int
    score_white: int
    move_count: int # Счетчик всех сделанных ходов
    last_score_change_move: int  # Номер хода, когда последний раз изменился счет
