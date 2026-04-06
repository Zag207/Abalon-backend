from core.movement.moving_directions import MovingDirections


class DeltaCoords:
    delta_line: int
    delta_diagonal: int

    def __init__(self, delta_line: int, delta_diagonal: int) -> None:
        self.delta_diagonal = delta_diagonal
        self.delta_line = delta_line

    @staticmethod
    def get_delta_coords_from_moving(
            moving_direction: MovingDirections
            ) -> DeltaCoords:
        moving_vector = MovingDirections.get_moving_vector(moving_direction)
        
        return DeltaCoords(moving_vector[0], moving_vector[1])