from core.geometry.circle_coords import CircleCoords
from core.board.circle_team import CircleTeam
import uuid

from core.geometry.delta_coords import DeltaCoords

class Circle:
    circle_id: uuid.UUID
    coords: CircleCoords
    circle_type: CircleTeam

    def __init__(
            self,
            coords: CircleCoords,
            circle_type: CircleTeam
            ) -> None:
        self.coords = coords
        self.circle_id = uuid.uuid6()
        self.circle_type = circle_type
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        
        return self.circle_type == other.circle_type and self.coords == other.coords

    def update_coords(self, deltaCoords: DeltaCoords) -> None:
        self.coords = self.coords.get_new_coords(deltaCoords)