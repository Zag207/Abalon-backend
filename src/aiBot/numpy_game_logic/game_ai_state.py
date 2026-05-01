from dataclasses import dataclass

import numpy as np


@dataclass
class NumpyAbalonGameState:
    board: np.ndarray  # 9x9 matrix representation of the board
    score_black: int = 0
    score_white: int = 0
    move_count: int = 0 # Счетчик всех сделанных ходов
    last_score_change_move: int = 0  # Номер хода, когда последний раз изменился счет
