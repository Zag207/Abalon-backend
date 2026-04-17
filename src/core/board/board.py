from dataclasses import dataclass, field
from typing import List
from uuid import UUID
from core.board.circle import Circle
from core.board.circle_team import CircleTeam, get_enemy_team
from core.board.move_utils import update_circle_move_linear, update_circle_move_parall
from core.geometry.circle_coords import CircleCoords
from core.geometry.delta_coords import DeltaCoords
from core.movement.moving_directions import MovingDirections
from core.movement.moving_types import MovingTypes

class Board:
    circles: List[Circle]

    def __init__(self, circles: List[Circle]) -> None:
        self.circles = circles
    
    def is_hex_empty(self, hex_coords: CircleCoords) -> bool:
        return not any(circle.coords == hex_coords for circle in self.circles)
    
    @staticmethod
    def get_diagonal_limits_for_line(line: int) -> DiagonalLimits:
        res = DiagonalLimits(diagonal_start=-1, diagonal_end=-1)

        if 0 < line <= 5:
            line -= 1
            res.diagonal_end = 9
            res.diagonal_start = 5 - line
        elif 5 < line <= 9:
            line = 9 - line
            res.diagonal_start = 1
            res.diagonal_end = 5 + line

        return res

    @staticmethod
    def is_in_board(coords: CircleCoords) -> bool:
        diagonal_limits_start = Board.get_diagonal_limits_for_line(coords.line).diagonal_start
        diagonal_limits_end = Board.get_diagonal_limits_for_line(coords.line).diagonal_end

        return (
            1 <= coords.line <= 9 and
            diagonal_limits_start <= coords.diagonal <= diagonal_limits_end
        )

    def get_circle_line(self, circle_checked: Circle, moving: MovingDirections) -> List[Circle]:
        if circle_checked is None:
            return []
        
        delta_coords = DeltaCoords.get_delta_coords_from_moving(moving)
        circle_line = [circle_checked]

        next_coords = circle_line[-1].coords.get_new_coords(delta_coords)

        while self.is_in_board(next_coords) and not self.is_hex_empty(next_coords):
            circle_line.append(
                next(circle for circle in self.circles if circle.coords == next_coords) # Подумать над оптимизацией
                )
            next_coords = circle_line[-1].coords.get_new_coords(delta_coords)

        return circle_line

    def check_for_linear(
            self,
            circle_line: List[Circle],
            moving: MovingDirections,
            current_team: CircleTeam,
            enemy_team: CircleTeam
            ) -> bool:
        if len(circle_line) == 0:
            return False

        res = True
        delta_coords = DeltaCoords.get_delta_coords_from_moving(moving)

        # Поменять на count?
        my_team_circle_count = sum(1 for circle in circle_line if circle.circle_type == current_team)
        enemy_circle_count = sum(1 for circle in circle_line if circle.circle_type == enemy_team)

        is_end_board = not self.is_in_board(
            circle_line[-1].coords.get_new_coords(delta_coords)
        )

        last_my_circle = next(
            (circle for circle in reversed(circle_line) if circle.circle_type == current_team),
            None
        )

        if not last_my_circle:
            return False

        if my_team_circle_count > 3:
            res = res and False
        elif enemy_circle_count > 0:
            if enemy_circle_count >= my_team_circle_count:
                res = res and False

            first_enemy_coords = next(
                (circle.coords for circle in circle_line if circle.circle_type == enemy_team)
            )
            expected_enemy_coords = last_my_circle.coords.get_new_coords(delta_coords)

            if (
                first_enemy_coords.line != expected_enemy_coords.line
                or first_enemy_coords.diagonal != expected_enemy_coords.diagonal
            ):
                res = res and False
        elif enemy_circle_count == 0 and is_end_board:
            res = res and False
        else:
            res = res and True

        return res

    def check_for_parall(
            self,
            circles_checked: List[Circle],
            moving: MovingDirections
            ) -> bool:
        if len(circles_checked) == 0:
            return False

        line = circles_checked[0].coords.line
        diagonal = circles_checked[0].coords.diagonal

        is_one_line = all(circle.coords.line == line for circle in circles_checked)
        is_one_diagonal = all(circle.coords.diagonal == diagonal for circle in circles_checked)

        sorted_circles_checked = sorted(circles_checked, key=lambda c: c.coords.diagonal)

        # Проверка диагонального проседания
        is_one_other_diagonal = True
        for i in range(1, len(sorted_circles_checked)):
            line_dist = sorted_circles_checked[i].coords.line - sorted_circles_checked[i - 1].coords.line
            diagonal_dist = sorted_circles_checked[i].coords.diagonal - sorted_circles_checked[i - 1].coords.diagonal
            status = (-1 <= line_dist <= 0) and (diagonal_dist == 1 or diagonal_dist == 0)
            if not status:
                is_one_other_diagonal = False
                break

        res = is_one_line or is_one_diagonal or is_one_other_diagonal

        # Проверка, свободна ли лунка по направлению движения
        delta_coords = DeltaCoords.get_delta_coords_from_moving(moving)
        res = res and all(
            self.is_in_board(circle.coords.get_new_coords(delta_coords)) and
            self.is_hex_empty(circle.coords.get_new_coords(delta_coords))
            for circle in circles_checked
        )

        # Проверка, находятся ли фишки рядом
        sorted_circles_checked = sorted(circles_checked, key=lambda c: c.coords.get_distance(circles_checked[0].coords))
        res = res and all(
            sorted_circles_checked[i].coords.get_distance(sorted_circles_checked[i + 1].coords) <= 1
            for i in range(len(sorted_circles_checked) - 1)
        )

        return res

    def get_moving_type(self, circles_checked_count: int) -> MovingTypes:
        res = MovingTypes.NoMove

        if circles_checked_count == 1:
            res = MovingTypes.Linear
        elif circles_checked_count > 1:
            res = MovingTypes.Parall
        
        return res

    def get_move_validation_result(
            self,
            circles_checked: List[Circle],
            move_direction: MovingDirections,
            current_team: CircleTeam,
            moving_type: MovingTypes
    ) -> tuple[bool, List[Circle]]:
        if moving_type == MovingTypes.Parall:
            is_good_move = self.check_for_parall(circles_checked, move_direction)
            return is_good_move, []

        if moving_type == MovingTypes.Linear:
            circle_line = self.get_circle_line(circles_checked[0], move_direction)
            is_good_move = self.check_for_linear(
                circle_line,
                move_direction,
                current_team,
                get_enemy_team(current_team)
            )
            return is_good_move, circle_line

        return False, []

    def get_circles_by_ids(self, circles_ids: List[UUID]) -> List[Circle]:
        return [circle for circle in self.circles if circle.circle_id in circles_ids]

    def move(
            self,
            circles_checked: List[Circle],
            move_direction: MovingDirections,
            current_team: CircleTeam
    ) -> MoveResult:
        if any(circle not in self.circles for circle in circles_checked):
            return MoveResult(is_error=True)
        
        moving_type = self.get_moving_type(len(circles_checked))
        increasing_score = 0

        if moving_type == MovingTypes.Parall:
            is_good_move, _ = self.get_move_validation_result(
                circles_checked,
                move_direction,
                current_team,
                moving_type
            )
            moving_circles = []

            if is_good_move:
                circles_checked_ids = [circle.circle_id for circle in circles_checked]

                self.circles = list(map(
                    lambda c: update_circle_move_parall(
                        c,
                        circles_checked_ids,
                        DeltaCoords.get_delta_coords_from_moving(move_direction),
                        moving_circles
                        ),
                    self.circles
                    ))
            
            return MoveResult(
                is_error=not is_good_move,
                increasing_score=increasing_score,
                circles_moving=moving_circles
            )
        elif moving_type == MovingTypes.Linear:
            is_good_move, circle_line = self.get_move_validation_result(
                circles_checked,
                move_direction,
                current_team,
                moving_type
                )
            moving_circles = []
            
            if is_good_move:
                circle_line_ids = [circle.circle_id for circle in circle_line]
                delta_coords = DeltaCoords.get_delta_coords_from_moving(move_direction)
                new_circles = []

                for circle in self.circles:
                    updated_circle, score_delta = update_circle_move_linear(
                        circle,
                        circle_line_ids,
                        delta_coords,
                        self.is_in_board,
                        moving_circles,
                    )
                    increasing_score = increasing_score or score_delta # только 1 очко, так как за один ход может вылезти одна фишка

                    if updated_circle is not None:
                        new_circles.append(updated_circle)

                self.circles = new_circles # присваиваю новый массив, так как фишки могут удаляться

            return MoveResult(
                is_error=not is_good_move,
                increasing_score=increasing_score,
                circles_moving=moving_circles
            )
        else:
            return MoveResult(is_error=True)

        

@dataclass
class DiagonalLimits:
    diagonal_start: int
    diagonal_end: int

@dataclass
class MoveResult:
    is_error: bool
    increasing_score: int = 0
    circles_moving: List[Circle] = field(default_factory=list)
