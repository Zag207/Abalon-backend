import pytest

from core.geometry.delta_coords import DeltaCoords
from core.movement.moving_directions import MovingDirections
from core.geometry.circle_coords import CircleCoords


class TestCoords:
    @pytest.mark.parametrize(
        "direction, expected_line, expected_diagonal",
        [
            (MovingDirections.NoMove, 0, 0),
            (MovingDirections.UpRight, -1, 1),
            (MovingDirections.Right, 0, 1),
            (MovingDirections.DownRight, 1, 0),
            (MovingDirections.DownLeft, 1, -1),
            (MovingDirections.Left, 0, -1),
            (MovingDirections.UpLeft, -1, 0),
        ],
    )
    def test_delta_coords(self, direction, expected_line, expected_diagonal):
        delta_coords = DeltaCoords.get_delta_coords_from_moving(direction)
        assert delta_coords.delta_line == expected_line
        assert delta_coords.delta_diagonal == expected_diagonal
    
    def test_get_new_coords(self):
        delta_coords = DeltaCoords.get_delta_coords_from_moving(MovingDirections.UpRight)
        coords = CircleCoords(5, 6)
        new_coords = coords.get_new_coords(delta_coords)

        assert(new_coords.line == 4)
        assert(new_coords.diagonal == 7)
    
    def test_get_distance(self):
        coords1 = CircleCoords(5, 6)
        coords2 = CircleCoords(2, 4)

        distance = coords1.get_distance(coords2)

        assert(distance == 3)
