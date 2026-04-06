import pytest

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords

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