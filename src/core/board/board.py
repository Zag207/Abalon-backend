from dataclasses import dataclass
from typing import List
from uuid import UUID
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.geometry.delta_coords import DeltaCoords
from core.movement.moving_directions import MovingDirections


class Board:
    circles: List[Circle]

    def __init__(self, circles: List[Circle]) -> None:
        self.circles = circles
    
    def is_hex_empty(self, hex_coords: CircleCoords) -> bool:
        return not any(circle.coords == hex_coords for circle in self.circles)
    
    def get_diagonal_limits_for_line(self, line: int) -> DiagonalLimits:
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

    def is_in_board(self, coords: CircleCoords) -> bool:
        diagonal_limits_start = self.get_diagonal_limits_for_line(coords.line).diagonal_start
        diagonal_limits_end = self.get_diagonal_limits_for_line(coords.line).diagonal_end

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

    # def move(
    #         self,
    #         circle_checked_ids: List[UUID],
    #         move_direction: MovingDirections,
    #         current_team: CircleTeam
    # ) -> MoveResult:
    #     circle_checked = 

@dataclass
class DiagonalLimits:
    diagonal_start: int
    diagonal_end: int

# @dataclass
# class MoveResult:
#     is_error: bool
#     increasing_score: int
