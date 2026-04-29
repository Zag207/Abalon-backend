from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import List
from uuid import UUID

from numpy import cross

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam, get_enemy_team
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections

WINNER_SCORE = 6
MAX_MOVES = 200  # Ограничение в 200 ходов суммарно
MOVES_LIMIT_VALUE = 0.8  # Value при завершении по лимиту ходов

log = logging.getLogger(__name__)

file_handler = logging.FileHandler('app2.log')
log.addHandler(file_handler)

@dataclass
class MovingResState:
    is_error: bool
    is_win: bool
    circles_moving: List[Circle] = field(default_factory=list)

class GameState:
    board: Board
    score_black: int
    score_white: int
    curr_team: CircleTeam
    move_count: int  # Счетчик всех сделанных ходов
    last_score_change_move: int  # Номер хода, когда последний раз изменился счет

    def __init__(self, circles: List[Circle]) -> None:
        self.board = Board(circles)
        self.curr_team = CircleTeam.White
        self.score_black = 0
        self.score_white = 0
        self.move_count = 0
        self.last_score_change_move = 0

    def clone(self) -> "GameState":
        cloned_state = GameState([
            Circle(CircleCoords(circle.coords.line, circle.coords.diagonal), circle.circle_type)
            for circle in self.board.circles
        ])
        cloned_state.curr_team = self.curr_team
        cloned_state.score_black = self.score_black
        cloned_state.score_white = self.score_white
        cloned_state.move_count = self.move_count
        cloned_state.last_score_change_move = self.last_score_change_move
        return cloned_state
    
    def get_winner_team(self) -> CircleTeam | None:
        if self.score_black >= WINNER_SCORE:
            return CircleTeam.Black
        elif self.score_white >= WINNER_SCORE:
            return CircleTeam.White
        else:
            return None
    
    def is_win(self) -> bool:
        return self.score_black >= WINNER_SCORE or self.score_white >= WINNER_SCORE
    
    def is_moves_limit_reached(self) -> bool:
        """Проверяет, достигнут ли лимит в 200 ходов БЕЗ ИЗМЕНЕНИЯ СЧЕТА."""
        # Если счет не менялся с начала (last_score_change_move = 0) и уже 200 ходов
        # ИЛИ если с последнего изменения счета прошло 200 ходов
        moves_since_last_score = self.move_count - self.last_score_change_move
        return self.move_count >= MAX_MOVES and moves_since_last_score >= MAX_MOVES
    
    def is_game_ended(self) -> bool:
        """Проверяет, закончилась ли игра (победой или по лимиту ходов)."""
        return self.is_win() or self.is_moves_limit_reached()
    
    def get_game_end_type(self) -> str:
        """Возвращает тип окончания игры: 'score_win', 'moves_limit', или 'not_ended'."""
        if self.is_win():
            return 'score_win'
        elif self.is_moves_limit_reached():
            return 'moves_limit'
        else:
            return 'not_ended'
    
    def get_value_for_player(self, player_team: CircleTeam) -> float | None:
        """
        Возвращает value для указанного игрока в зависимости от типа окончания игры.
        
        Возвращает:
        - None: если игра еще не закончилась
        - 1.0/-1.0: традиционная победа (набрано 6 очков)
        - 0.8/-0.8: победа при лимите в 200 ходов
        - 0.0: ничья при лимите ходов (одинаковый счет)
        """
        if not self.is_game_ended():
            return None
        
        # Считаем колиество фишек за, на вражеской территрии для каждого игрока, чтобы использовать в случае ничьи при лимите ходов
        cross_center_count_black = self.board.get_circles_count_cross_center_line(CircleTeam.Black)
        cross_center_count_white = self.board.get_circles_count_cross_center_line(CircleTeam.White)

        if self.is_win():
            winner = self.get_winner_team()
            if winner == player_team:
                return 1.0
            else:
                return -1.0
        elif self.is_moves_limit_reached():
            # Сравниваем очки при лимите ходов
            if player_team == CircleTeam.Black:
                if self.score_black > self.score_white or cross_center_count_black > cross_center_count_white:
                    return MOVES_LIMIT_VALUE
                elif self.score_black < self.score_white or cross_center_count_black < cross_center_count_white:
                    return -MOVES_LIMIT_VALUE
                else:
                    return 0.0  # Ничья
            else:  # CircleTeam.White
                if self.score_white > self.score_black or cross_center_count_white > cross_center_count_black:
                    return MOVES_LIMIT_VALUE
                elif self.score_white < self.score_black or cross_center_count_white < cross_center_count_black:
                    return -MOVES_LIMIT_VALUE
                else:
                    return 0.0  # Ничья
        
        return None
    
    def get_moving_team(self) -> CircleTeam:
        return get_enemy_team(self.curr_team)

    def get_circles(self) -> List[Circle]:
        return self.board.circles

    def _make_move(self, 
                    circles_checked: List[Circle], 
                    move_direction: MovingDirections, 
                    moving_team: CircleTeam
                    ) -> MovingResState:
        if self.is_game_ended():
            return MovingResState(True, True, [])
        
        if moving_team != self.get_moving_team():
            return MovingResState(True, False, [])
        
        moving_res = self.board.move(circles_checked, move_direction, moving_team)

        if not moving_res.is_error:
            self.curr_team = moving_team

            if moving_res.increasing_score > 0:
                match moving_team:
                    case CircleTeam.Black:
                        self.score_black += 1
                    case CircleTeam.White:
                        self.score_white += 1
                    case _:
                        pass
                # Обновляем последний ход, когда был набран очко
                self.last_score_change_move = self.move_count
            
            # Увеличиваем счетчик ходов после успешного хода
            self.move_count += 1
        
        return MovingResState(moving_res.is_error, self.is_game_ended(), moving_res.circles_moving)

    def move(
            self,
            circles_checked_ids: List[UUID],
            move_direction: MovingDirections,
            moving_team: CircleTeam
            ) -> MovingResState:
        checked_circles = self.board.get_circles_by_ids(circles_checked_ids)

        if len(checked_circles) != len(circles_checked_ids):
            return MovingResState(True, False, [])

        return self._make_move(checked_circles, move_direction, moving_team)
