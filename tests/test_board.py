import pytest

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections

class TestBoard:
    ...

class TestBoardIsHexEmpty:
    def test_is_hex_empty_returns_true_for_empty_hex(self):
        circles = [
            Circle(CircleCoords(5, 6), CircleTeam.White),
            Circle(CircleCoords(3, 4), CircleTeam.Black),
        ]
        board = Board(circles)
        
        assert board.is_hex_empty(CircleCoords(1, 1)) is True

    def test_is_hex_empty_returns_false_for_occupied_hex(self):
        circles = [
            Circle(CircleCoords(5, 6), CircleTeam.White),
            Circle(CircleCoords(3, 4), CircleTeam.Black),
        ]
        board = Board(circles)
        
        assert board.is_hex_empty(CircleCoords(5, 6)) is False

    def test_is_hex_empty_on_empty_board(self):
        board = Board([])
        
        assert board.is_hex_empty(CircleCoords(5, 6)) is True

    def test_is_hex_empty_checks_all_circles(self):
        circles = [
            Circle(CircleCoords(1, 1), CircleTeam.White),
            Circle(CircleCoords(2, 2), CircleTeam.White),
            Circle(CircleCoords(3, 3), CircleTeam.Black),
        ]
        board = Board(circles)
        
        assert board.is_hex_empty(CircleCoords(3, 3)) is False
        assert board.is_hex_empty(CircleCoords(4, 4)) is True


class TestBoardGetDiagonalLimitsForLine:
    @pytest.mark.parametrize(
        "line, expected_start, expected_end",
        [
            (1, 5, 9),
            (2, 4, 9),
            (3, 3, 9),
            (4, 2, 9),
            (5, 1, 9),
            (6, 1, 8),
            (7, 1, 7),
            (8, 1, 6),
            (9, 1, 5),
            (0, -1, -1),
            (10, -1, -1),
            (-3, -1, -1),
        ],
    )
    def test_get_diagonal_limits_for_line(self, line, expected_start, expected_end):
        board = Board([])

        limits = board.get_diagonal_limits_for_line(line)

        assert limits.diagonal_start == expected_start
        assert limits.diagonal_end == expected_end


class TestBoardIsInBoard:
    @pytest.mark.parametrize(
        "line, diagonal",
        [
            (1, 5),
            (1, 9),
            (5, 1),
            (5, 9),
            (9, 1),
            (9, 5),
            (6, 8),
            (3, 7),
        ],
    )
    def test_is_in_board_returns_true_for_valid_coords(self, line, diagonal):
        board = Board([])

        assert board.is_in_board(CircleCoords(line, diagonal)) is True

    @pytest.mark.parametrize(
        "line, diagonal",
        [
            (0, 1),
            (10, 1),
            (-1, 5),
            (1, 4),
            (1, 10),
            (5, 0),
            (5, 10),
            (9, 0),
            (9, 6),
            (6, 9),
            (3, 2),
        ],
    )
    def test_is_in_board_returns_false_for_invalid_coords(self, line, diagonal):
        board = Board([])

        assert board.is_in_board(CircleCoords(line, diagonal)) is False


class TestBoardGetCircleLine:
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