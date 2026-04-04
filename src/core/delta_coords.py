from core.moving_directions import MovingDirections


class DeltaCoords:
    delta_line: int
    delta_diagonal: int

    def __init__(self, delta_line: int, delta_diagonal: int) -> None:
        self.delta_diagonal = delta_diagonal
        self.delta_line = delta_line

    def get_delta_coords_from_moving(
            self, 
            moving_direction: MovingDirections
            ) -> DeltaCoords:
        moving_transform_map = {
            MovingDirections.UpRight: DeltaCoords(-1, 1),
            MovingDirections.Right: DeltaCoords(0, 1),
            MovingDirections.DownRight: DeltaCoords(1, 0),
            MovingDirections.DownLeft: DeltaCoords(1, -1),
            MovingDirections.Left: DeltaCoords(0, -1),
            MovingDirections.UpLeft: DeltaCoords(-1, 0)
        }

        return moving_transform_map[moving_direction]