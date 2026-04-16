from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections


class TestBoardCheckForLinear:
    def test_check_for_linear_empty_circle_line(self):
        board = Board([])

        result = board.check_for_linear([], MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is False

    def test_check_for_linear_valid_capture_with_enemy_circles(self):
        my_circle = Circle(CircleCoords(5, 5), CircleTeam.White)
        my_circle_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        enemy_circle = Circle(CircleCoords(5, 7), CircleTeam.Black)
        circle_line = [my_circle, my_circle_2, enemy_circle]
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is True

    def test_check_for_linear_invalid_too_many_my_circles(self):
        my_circles = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(5, 6), CircleTeam.White),
            Circle(CircleCoords(5, 7), CircleTeam.White),
            Circle(CircleCoords(5, 8), CircleTeam.White),
        ]
        circle_line = my_circles
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is False

    def test_check_for_linear_invalid_too_many_enemy_circles(self):
        my_circles = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(5, 6), CircleTeam.White),
        ]
        enemy_circles = [
            Circle(CircleCoords(5, 7), CircleTeam.Black),
            Circle(CircleCoords(5, 8), CircleTeam.Black),
        ]
        circle_line = my_circles + enemy_circles
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is False

    def test_check_for_linear_invalid_enemy_not_consecutive(self):
        my_circles = [
            Circle(CircleCoords(5, 5), CircleTeam.White),
            Circle(CircleCoords(5, 6), CircleTeam.White),
        ]
        enemy_circle_wrong_place = [
            Circle(CircleCoords(5, 8), CircleTeam.Black),
        ]
        circle_line = my_circles + enemy_circle_wrong_place
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is False

    def test_check_for_linear_invalid_no_enemy_at_end_of_board(self):
        my_circles = [
            Circle(CircleCoords(1, 8), CircleTeam.White),
            Circle(CircleCoords(1, 9), CircleTeam.White),
        ]
        circle_line = my_circles
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is False

    def test_check_for_linear_invalid_no_last_my_circle(self):
        enemy_circles = [
            Circle(CircleCoords(5, 5), CircleTeam.Black),
            Circle(CircleCoords(5, 6), CircleTeam.Black),
        ]
        circle_line = enemy_circles
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is False

    def test_check_for_linear_valid_single_my_circle_without_enemy(self):
        my_circle = Circle(CircleCoords(5, 5), CircleTeam.White)
        circle_line = [my_circle]
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Right, CircleTeam.White, CircleTeam.Black)

        assert result is True
    
    def test_check_for_linear_invalid_circle_not_in_board(self):
        circle = Circle(CircleCoords(0, 0), CircleTeam.White)
        circle_line = [circle]
        board = Board(circle_line)

        result = board.check_for_linear(circle_line, MovingDirections.Left, CircleTeam.White, CircleTeam.Black)

        assert result is False
  