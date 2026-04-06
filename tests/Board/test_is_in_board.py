import pytest

from core.board.board import Board
from core.geometry.circle_coords import CircleCoords


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
