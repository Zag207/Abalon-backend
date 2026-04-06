from typing import Iterable, List

from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords


def fill_circle_line(
        line: int,
        startDiagonal: int,
        circlesCount: int,
        circleColor: CircleTeam
        ) -> Iterable[Circle]:
    end_diagonal = startDiagonal + circlesCount
    coords_list = [CircleCoords(line, diagonal) for diagonal in range(startDiagonal, end_diagonal)]
    circle_list = map(lambda coords: Circle(coords, circleColor), coords_list)

    return circle_list

def fill_circle_board() -> List[Circle]:
    circle_list = []

    circle_list.extend(fill_circle_line(1, 5, 5, CircleTeam.White))
    circle_list.extend(fill_circle_line(2, 4, 6, CircleTeam.White))
    circle_list.extend(fill_circle_line(3, 5, 3, CircleTeam.White))

    circle_list.extend(fill_circle_line(7, 3, 3, CircleTeam.Black))
    circle_list.extend(fill_circle_line(8, 1, 6, CircleTeam.Black))
    circle_list.extend(fill_circle_line(9, 1, 5, CircleTeam.Black))

    return circle_list
