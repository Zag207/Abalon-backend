from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections


class TestBoardGetCircleLine:
    def test_get_circle_line_returns_empty_list_when_circle_checked_none(self):
        board = Board([])
        res = board.get_circle_line(None, MovingDirections.DownLeft) # type: ignore

        assert res == []
        
    def test_get_circle_line_returns_only_checked_when_next_hex_is_empty(self):
        circle_checked = Circle(CircleCoords(5, 5), CircleTeam.White)
        board = Board([circle_checked])

        circle_line = board.get_circle_line(circle_checked, MovingDirections.Right)

        assert circle_line == [circle_checked]

    def test_get_circle_line_collects_consecutive_circles_in_direction(self):
        circle_checked = Circle(CircleCoords(5, 5), CircleTeam.White)
        next_circle_1 = Circle(CircleCoords(5, 6), CircleTeam.Black)
        next_circle_2 = Circle(CircleCoords(5, 7), CircleTeam.Black)
        board = Board([circle_checked, next_circle_1, next_circle_2])

        circle_line = board.get_circle_line(circle_checked, MovingDirections.Right)

        assert circle_line == [circle_checked, next_circle_1, next_circle_2]

    def test_get_circle_line_stops_when_next_coords_out_of_board(self):
        circle_checked = Circle(CircleCoords(1, 8), CircleTeam.White)
        edge_circle = Circle(CircleCoords(1, 9), CircleTeam.Black)
        board = Board([circle_checked, edge_circle])

        circle_line = board.get_circle_line(circle_checked, MovingDirections.Right)

        assert circle_line == [circle_checked, edge_circle]
