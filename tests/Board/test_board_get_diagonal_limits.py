import pytest

from core.board.board import Board


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
