from dataclasses import dataclass
from typing import List
from core.board.circle import Circle
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
        delta_coords = DeltaCoords.get_delta_coords_from_moving(moving)
        circle_line = [circle_checked]

        next_coords = circle_line[-1].coords.get_new_coords(delta_coords)

        while self.is_in_board(next_coords) and not self.is_hex_empty(next_coords):
            circle_line.append(
                next(circle for circle in self.circles if circle.coords == next_coords) # Подумать над оптимизацией
                )
            next_coords = circle_line[-1].coords.get_new_coords(delta_coords)

        return circle_line

@dataclass
class DiagonalLimits:
    diagonal_start: int
    diagonal_end: int

