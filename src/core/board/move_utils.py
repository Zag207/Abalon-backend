from __future__ import annotations

import copy
from typing import Callable, List, Optional
from uuid import UUID

from core.board.circle import Circle
from core.geometry.delta_coords import DeltaCoords


def update_circle_move_parall(
        circle: Circle,
        circles_checked_ids: List[UUID],
        delta_coords: DeltaCoords,
        moving_circles: List[Circle]
        ) -> Circle:
    if circle.circle_id in circles_checked_ids:
        new_coords = circle.coords.get_new_coords(delta_coords)
        circle.coords = new_coords

        moving_circles.append(copy.deepcopy(circle))

    return circle


def update_circle_move_linear(
        circle: Circle,
        circle_line_ids: List[UUID],
        delta_coords: DeltaCoords,
        is_in_board: Callable,
        moving_circles: List[Circle]
        ) -> tuple[Optional[Circle], int]:
    if circle.circle_id not in circle_line_ids:
        return circle, 0

    new_coords = circle.coords.get_new_coords(delta_coords)

    if not is_in_board(new_coords):
        return None, 1

    circle.coords = new_coords
    moving_circles.append(copy.deepcopy(circle))

    return circle, 0
