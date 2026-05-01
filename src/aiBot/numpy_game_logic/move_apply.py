import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from typing import List

from core.geometry.circle_coords import CircleCoords
from core.geometry.delta_coords import DeltaCoords
from core.board.board import Board
from core.movement.moving_directions import MovingDirections
from core.movement.moving_types import MovingTypes


@dataclass
class MoveApplyResult:
    board: npt.NDArray[np.int8]
    score_delta: int


def apply_move_to_board(
        board: npt.NDArray[np.int8],
        selected_coords: List[CircleCoords],
        direction: MovingDirections,
        player_code: int
        ) -> MoveApplyResult:
    """
    Применяет ход к numpy-доске Абалона.
    
    Args:
        board: текущее состояние доски (9x9 матрица)
        selected_coords: координаты выбранных фишек для перемещения
        direction: направление движения
        player_code: код игрока (1 для White, -1 для Black)
    
    Returns:
        MoveApplyResult с новой доской и количеством добавленных очков
    """
    new_board = board.copy()
    score_delta = 0
    enemy_code = -player_code
    
    # Вычисляем вектор движения
    delta_coords = DeltaCoords.get_delta_coords_from_moving(direction)
    delta_line = delta_coords.delta_line
    delta_diag = delta_coords.delta_diagonal
    
    moving_type = Board.get_moving_type(len(selected_coords))
    
    if moving_type == MovingTypes.Parall:
        # Параллельный ход: просто двигаем все фишки на одну позицию
        for coords in selected_coords:
            # Удаляем со старой позиции
            new_board[coords.line - 1, coords.diagonal - 1] = 0
        
        # Добавляем на новые позиции
        for coords in selected_coords:
            new_coords = coords.get_new_coords(delta_coords)
            new_board[new_coords.line - 1, new_coords.diagonal - 1] = player_code
    
    elif moving_type == MovingTypes.Linear:
        # Линейный ход: собираем цепочку СВОИХ фишек, потом смотрим врагов
        # Начинаем с выбранной фишки и ищем своих подряд в направлении хода
        
        # Собираем цепочку своих фишек с доски
        my_chain = []
        cursor = selected_coords[0]
        
        # Идём в направлении хода и собираем своих
        while Board.is_in_board(cursor) and new_board[cursor.line - 1, cursor.diagonal - 1] == player_code:
            my_chain.append(cursor)
            cursor = cursor.get_new_coords(delta_coords)
        
        # После последней своей ищем врагов
        enemies_to_move = []
        while Board.is_in_board(cursor) and new_board[cursor.line - 1, cursor.diagonal - 1] == enemy_code:
            enemies_to_move.append(cursor)
            cursor = cursor.get_new_coords(delta_coords)
        
        # Есть ли куда толкать врагов
        if enemies_to_move:
            push_target = cursor  # Позиция после последнего врага
            
            # Если толкаем врага за доску, добавляем очко
            if not Board.is_in_board(push_target):
                score_delta = 1
                # Удаляем последнего врага (вышедшего за доску)
                last_enemy = enemies_to_move[-1]
                new_board[last_enemy.line - 1, last_enemy.diagonal - 1] = 0
                enemies_to_move.pop()
            
            # Двигаем врагов на одну позицию в направлении (в обратном порядке чтобы не затереть)
            for i in range(len(enemies_to_move) - 1, -1, -1):
                old_coords = enemies_to_move[i]
                new_coords = old_coords.get_new_coords(delta_coords)
                new_board[new_coords.line - 1, new_coords.diagonal - 1] = enemy_code
                new_board[old_coords.line - 1, old_coords.diagonal - 1] = 0
        
        # Двигаем свою цепочку на одну позицию (в обратном порядке чтобы не затереть)
        for i in range(len(my_chain) - 1, -1, -1):
            old_coords = my_chain[i]
            new_board[old_coords.line - 1, old_coords.diagonal - 1] = 0
            new_coords = old_coords.get_new_coords(delta_coords)
            new_board[new_coords.line - 1, new_coords.diagonal - 1] = player_code
    
    return MoveApplyResult(board=new_board, score_delta=score_delta)
