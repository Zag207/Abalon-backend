from typing import List
from core.board.circle import Circle
from core.geometry.circle_coords import CircleCoords


class Board:
    circles: List[Circle]

    def __init__(self, circles: List[Circle]) -> None:
        self.circles = circles
    
    def is_hex_empty(self, hex_coords: CircleCoords) -> bool:
        return not any(circle.coords == hex_coords for circle in self.circles)