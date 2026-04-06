from dataclasses import dataclass
from typing import List
from core.board.circle import Circle
from core.geometry.circle_coords import CircleCoords


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

@dataclass
class DiagonalLimits:
    diagonal_start: int
    diagonal_end: int

