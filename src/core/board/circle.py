from core.geometry.circle_coords import CircleCoords
from core.board.circle_team import CircleTeam
import uuid

from core.geometry.delta_coords import DeltaCoords

class Circle:
    circle_id: uuid.UUID
    coords: CircleCoords
    is_checked: bool
    is_moving: bool
    circle_type: CircleTeam

    def __init__(
            self,
            coords: CircleCoords,
            circle_type: CircleTeam,
            is_checked: bool = False,
            is_moving: bool = False
            ) -> None:
        self.coords = coords
        self.circle_id = uuid.uuid6()
        self.is_checked = is_checked
        self.is_moving = is_moving
        self.circle_type = circle_type

    def update_coords(self, deltaCoords: DeltaCoords) -> None:
        self.coords = self.coords.get_new_coords(deltaCoords)