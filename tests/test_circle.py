
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.geometry.delta_coords import DeltaCoords
from core.movement.moving_directions import MovingDirections


class TestCircle():
    def test_update_coords(self):
        circle_coords = CircleCoords(5, 6)
        circle = Circle(circle_coords, CircleTeam.White)
        delta_coords = DeltaCoords.get_delta_coords_from_moving(MovingDirections.DownLeft)
        circle.update_coords(delta_coords)
        new_coords = circle_coords.get_new_coords(delta_coords)

        assert(circle.coords == new_coords)