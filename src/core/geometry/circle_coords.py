from core.geometry.delta_coords import DeltaCoords


class CircleCoords:
    diagonal: int
    line: int

    def __init__(self, line: int, diagonal: int) -> None:
        self.diagonal = diagonal
        self.line = line
    
    def get_distance(self, coords: CircleCoords) -> int:
        diagonal_dist = abs(self.diagonal - coords.diagonal)
        line_dist = abs(self.line - coords.line)
        
        return max(diagonal_dist, line_dist)
    
    def get_new_coords(self, delta_coords: DeltaCoords) -> CircleCoords:
        return CircleCoords(
            self.line + delta_coords.delta_line,
            self.diagonal + delta_coords.delta_diagonal
            )