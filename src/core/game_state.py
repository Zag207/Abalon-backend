from dataclasses import dataclass, field
import logging
from typing import List
from uuid import UUID

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam, get_enemy_team
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections

WINNER_SCORE = 6

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

    def __init__(self, circles: List[Circle]) -> None:
        self.board = Board(circles)
        self.curr_team = CircleTeam.White
        self.score_black = 0
        self.score_white = 0

    def clone(self) -> "GameState":
        cloned_state = GameState([
            Circle(CircleCoords(circle.coords.line, circle.coords.diagonal), circle.circle_type)
            for circle in self.board.circles
        ])
        cloned_state.curr_team = self.curr_team
        cloned_state.score_black = self.score_black
        cloned_state.score_white = self.score_white
        return cloned_state
    
    def get_winner_team(self) -> CircleTeam | None:
        if self.score_black >= WINNER_SCORE:
            return CircleTeam.Black
        elif self.score_white >= WINNER_SCORE:
            return CircleTeam.White
        else:
            return None
    
    def is_win(self) -> bool:
        log.info(f"Checking win condition. Black: {self.score_black}, White: {self.score_white}")

        return self.score_black >= WINNER_SCORE or self.score_white >= WINNER_SCORE
    
    def get_moving_team(self) -> CircleTeam:
        return get_enemy_team(self.curr_team)

    def get_circles(self) -> List[Circle]:
        return self.board.circles

    def move(
            self,
            circles_checked_ids: List[UUID],
            move_direction: MovingDirections,
            moving_team: CircleTeam
            ) -> MovingResState:
        if self.is_win():
            return MovingResState(True, True, [])

        if moving_team != self.get_moving_team():
            return MovingResState(True, False, [])

        checked_circles = self.board.get_circles_by_ids(circles_checked_ids)

        if len(checked_circles) != len(circles_checked_ids):
            return MovingResState(True, False, [])

        moving_res = self.board.move(checked_circles, move_direction, moving_team)

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
        
        return MovingResState(moving_res.is_error, self.is_win(), moving_res.circles_moving)
