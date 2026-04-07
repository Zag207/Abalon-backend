from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections


class TestBoardCheckForParall:
    def test_check_for_parall_valid_same_line(self):
        circles_checked = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(5, 6), CircleTeam.White),
        ]
        board = Board(circles_checked)

        result = board.check_for_parall(circles_checked, MovingDirections.UpRight)

        assert result is True

    def test_check_for_parall_valid_same_diagonal(self):
        circles_checked = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(6, 5), CircleTeam.White),
        ]
        board = Board(circles_checked)

        result = board.check_for_parall(circles_checked, MovingDirections.Right)

        assert result is True

    def test_check_for_parall_invalid_not_adjacent(self):
        circles_checked = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(5, 7), CircleTeam.White),
        ]
        board = Board(circles_checked)

        result = board.check_for_parall(circles_checked, MovingDirections.Right)

        assert result is False

    def test_check_for_parall_invalid_next_hex_occupied(self):
        circles_checked = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(5, 6), CircleTeam.White),
        ]
        occupied_circle = Circle(CircleCoords(4, 6), CircleTeam.Black)
        board = Board(circles_checked + [occupied_circle])

        result = board.check_for_parall(circles_checked, MovingDirections.UpRight)

        assert result is False

    def test_check_for_parall_invalid_next_hex_out_of_board(self):
        circles_checked = [
            Circle(CircleCoords(1, 8), CircleTeam.White),
            Circle(CircleCoords(1, 9), CircleTeam.White),
        ]
        board = Board(circles_checked)

        result = board.check_for_parall(circles_checked, MovingDirections.Right)

        assert result is False

    def test_check_for_parall_invalid_not_aligned(self):
        circles_checked = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(6, 7), CircleTeam.White),
        ]
        board = Board(circles_checked)

        result = board.check_for_parall(circles_checked, MovingDirections.Right)

        assert result is False
