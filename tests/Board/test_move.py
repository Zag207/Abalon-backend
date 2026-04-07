from uuid import uuid4

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections

class TestMove:
    def test_move_returns_error_when_checked_id_missing(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        board = Board([white])

        result = board.move([uuid4()], MovingDirections.Right, CircleTeam.White)

        assert result.is_error is True
        assert result.increasing_score == 0
        assert len(result.circles_moving) == 0

    def test_move_parallel_valid_updates_checked_circles(self):
        white_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        white_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        board = Board([white_1, white_2])

        result = board.move(
            [white_1.circle_id, white_2.circle_id],
            MovingDirections.UpRight,
            CircleTeam.White,
        )

        assert result.is_error is False
        assert result.increasing_score == 0
        assert len(result.circles_moving) == 2
        assert {
            (c.coords.line, c.coords.diagonal) for c in board.circles
            } == {(4, 6), (4, 7)}

    def test_move_parallel_invalid_keeps_board_state(self):
        white_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        white_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        blocker = Circle(CircleCoords(4, 6), CircleTeam.Black)
        board = Board([white_1, white_2, blocker])

        result = board.move(
            [white_1.circle_id, white_2.circle_id],
            MovingDirections.UpRight,
            CircleTeam.White,
        )

        assert result.is_error is True
        assert result.increasing_score == 0
        assert len(result.circles_moving) == 0
        assert {
            (c.coords.line, c.coords.diagonal) for c in board.circles
            } == {(5, 5), (5, 6), (4, 6)}

    def test_move_linear_valid_push_inside_board(self):
        white_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        white_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        black = Circle(CircleCoords(5, 7), CircleTeam.Black)
        board = Board([white_1, white_2, black])

        result = board.move([white_1.circle_id], MovingDirections.Right, CircleTeam.White)

        assert result.is_error is False
        assert result.increasing_score == 0
        assert len(result.circles_moving) == 3
        assert {
            (c.coords.line, c.coords.diagonal) for c in board.circles
            } == {(5, 6), (5, 7), (5, 8)}

    def test_move_linear_valid_push_out_of_board_increases_score(self):
        white_1 = Circle(CircleCoords(1, 7), CircleTeam.White)
        white_2 = Circle(CircleCoords(1, 8), CircleTeam.White)
        black = Circle(CircleCoords(1, 9), CircleTeam.Black)
        board = Board([white_1, white_2, black])

        result = board.move([white_1.circle_id], MovingDirections.Right, CircleTeam.White)

        assert result.is_error is False
        assert result.increasing_score == 1
        assert len(result.circles_moving) == 2
        assert len(board.circles) == 2
        assert {
            (c.coords.line, c.coords.diagonal) for c in board.circles
            } == {(1, 8), (1, 9)}

    def test_move_linear_invalid_when_enemy_not_weaker(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        black = Circle(CircleCoords(5, 6), CircleTeam.Black)
        board = Board([white, black])

        result = board.move([white.circle_id], MovingDirections.Right, CircleTeam.White)

        assert result.is_error is True
        assert result.increasing_score == 0
        assert len(result.circles_moving) == 0
        assert {
            (c.coords.line, c.coords.diagonal) for c in board.circles
            } == {(5, 5), (5, 6)}
    
    def test_move_linear_invalid_when_enemy_is_more(self):
        white1 = Circle(CircleCoords(7, 3), CircleTeam.White)
        black1 = Circle(CircleCoords(6, 4), CircleTeam.Black)
        black2 = Circle(CircleCoords(5, 5), CircleTeam.Black)
        board = Board([white1, black1, black2])

        result = board.move([white1.circle_id], MovingDirections.UpRight, CircleTeam.White)

        assert result.is_error is True
        assert result.increasing_score == 0
        assert len(result.circles_moving) == 0
        assert {
            (c.coords.line, c.coords.diagonal) for c in board.circles
            } == {(7, 3), (6, 4), (5, 5)}
    
    def test_move_linear_valid_when_between_enemies_void(self):
        white1 = Circle(CircleCoords(7, 3), CircleTeam.White)
        white2 = Circle(CircleCoords(6, 4), CircleTeam.White)
        black1 = Circle(CircleCoords(5, 5), CircleTeam.Black)
        black2 = Circle(CircleCoords(3, 7), CircleTeam.Black)
        board = Board([white1, white2, black1, black2])

        result = board.move(
            [white1.circle_id],
            MovingDirections.UpRight,
            CircleTeam.White
            )
        
        assert result.is_error is False
        assert result.increasing_score == 0
        assert len(result.circles_moving) == 3
        assert {
            (c.coords.line, c.coords.diagonal) for c in board.circles
            } == {(6, 4), (5, 5), (4, 6), (3, 7)}
