from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections
from core.movement.moving_types import MovingTypes


class TestBoardGetMoveValidationResult:
    def test_get_move_validation_result_parall_valid(self):
        white_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        white_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        board = Board([white_1, white_2])

        is_good_move, circle_line = board.get_move_validation_result(
            circles_checked=[white_1, white_2],
            move_direction=MovingDirections.UpRight,
            current_team=CircleTeam.White,
            moving_type=MovingTypes.Parall,
        )

        assert is_good_move is True
        assert circle_line == []

    def test_get_move_validation_result_linear_valid(self):
        white_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        white_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        black = Circle(CircleCoords(5, 7), CircleTeam.Black)
        board = Board([white_1, white_2, black])

        is_good_move, circle_line = board.get_move_validation_result(
            circles_checked=[white_1],
            move_direction=MovingDirections.Right,
            current_team=CircleTeam.White,
            moving_type=MovingTypes.Linear,
        )

        assert is_good_move is True
        assert [(c.coords.line, c.coords.diagonal) for c in circle_line] == [(5, 5), (5, 6), (5, 7)]

    def test_get_move_validation_result_linear_invalid(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        black = Circle(CircleCoords(5, 6), CircleTeam.Black)
        board = Board([white, black])

        is_good_move, circle_line = board.get_move_validation_result(
            circles_checked=[white],
            move_direction=MovingDirections.Right,
            current_team=CircleTeam.White,
            moving_type=MovingTypes.Linear,
        )

        assert is_good_move is False
        assert [(c.coords.line, c.coords.diagonal) for c in circle_line] == [(5, 5), (5, 6)]

    def test_get_move_validation_result_linear_accepts_new_ids_in_checked_circles(self):
        board_white_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        board_white_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        board_black = Circle(CircleCoords(5, 7), CircleTeam.Black)
        board = Board([board_white_1, board_white_2, board_black])

        checked_circle_with_new_id = Circle(CircleCoords(5, 5), CircleTeam.White)
        board_ids = {c.circle_id for c in board.circles}

        is_good_move, circle_line = board.get_move_validation_result(
            circles_checked=[checked_circle_with_new_id],
            move_direction=MovingDirections.Right,
            current_team=CircleTeam.White,
            moving_type=MovingTypes.Linear,
        )

        assert checked_circle_with_new_id.circle_id not in board_ids
        assert is_good_move is True
        assert circle_line[0].circle_id == checked_circle_with_new_id.circle_id
        assert [(c.coords.line, c.coords.diagonal) for c in circle_line] == [(5, 5), (5, 6), (5, 7)]

    def test_get_move_validation_result_parall_accepts_new_ids_in_checked_circles(self):
        board_white_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        board_white_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        board = Board([board_white_1, board_white_2])

        checked_with_new_id_1 = Circle(CircleCoords(5, 5), CircleTeam.White)
        checked_with_new_id_2 = Circle(CircleCoords(5, 6), CircleTeam.White)
        board_ids = {c.circle_id for c in board.circles}

        is_good_move, circle_line = board.get_move_validation_result(
            circles_checked=[checked_with_new_id_1, checked_with_new_id_2],
            move_direction=MovingDirections.UpRight,
            current_team=CircleTeam.White,
            moving_type=MovingTypes.Parall,
        )

        assert checked_with_new_id_1.circle_id not in board_ids
        assert checked_with_new_id_2.circle_id not in board_ids
        assert is_good_move is True
        assert circle_line == []

    def test_get_move_validation_result_no_move_returns_false(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        board = Board([white])

        is_good_move, circle_line = board.get_move_validation_result(
            circles_checked=[white],
            move_direction=MovingDirections.Right,
            current_team=CircleTeam.White,
            moving_type=MovingTypes.NoMove,
        )

        assert is_good_move is False
        assert circle_line == []
