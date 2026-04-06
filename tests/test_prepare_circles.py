from core.board.circle_team import CircleTeam
from core.setup.prepare_circles import fill_circle_board, fill_circle_line


class TestPrepareCirclesUtils:
    def test_fill_circle_line_creates_expected_circles(self):
        circles = list(fill_circle_line(2, 4, 3, CircleTeam.White))

        assert len(circles) == 3
        assert [circle.coords.line for circle in circles] == [2, 2, 2]
        assert [circle.coords.diagonal for circle in circles] == [4, 5, 6]
        assert [circle.circle_type for circle in circles] == [
            CircleTeam.White,
            CircleTeam.White,
            CircleTeam.White,
        ]

    def test_fill_circle_board_creates_full_initial_setup(self):
        circles = fill_circle_board()

        assert len(circles) == 28
        assert len([circle for circle in circles if circle.circle_type == CircleTeam.White]) == 14
        assert len([circle for circle in circles if circle.circle_type == CircleTeam.Black]) == 14

        white_positions = {
            (circle.coords.line, circle.coords.diagonal)
            for circle in circles
            if circle.circle_type == CircleTeam.White
        }
        black_positions = {
            (circle.coords.line, circle.coords.diagonal)
            for circle in circles
            if circle.circle_type == CircleTeam.Black
        }

        assert white_positions == {
            (1, 5),
            (1, 6),
            (1, 7),
            (1, 8),
            (1, 9),
            (2, 4),
            (2, 5),
            (2, 6),
            (2, 7),
            (2, 8),
            (2, 9),
            (3, 5),
            (3, 6),
            (3, 7),
        }

        assert black_positions == {
            (7, 3),
            (7, 4),
            (7, 5),
            (8, 1),
            (8, 2),
            (8, 3),
            (8, 4),
            (8, 5),
            (8, 6),
            (9, 1),
            (9, 2),
            (9, 3),
            (9, 4),
            (9, 5),
        }
