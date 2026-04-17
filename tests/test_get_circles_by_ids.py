from uuid import uuid4

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords


class TestGetCirclesByIds:
    def test_returns_circles_for_existing_ids(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        black = Circle(CircleCoords(4, 6), CircleTeam.Black)
        board = Board([white, black])

        result = board.get_circles_by_ids([white.circle_id, black.circle_id])

        assert result == [white, black]

    def test_returns_only_matching_circles_when_some_ids_are_missing(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        black = Circle(CircleCoords(4, 6), CircleTeam.Black)
        board = Board([white, black])

        result = board.get_circles_by_ids([white.circle_id, uuid4()])

        assert result == [white]

    def test_returns_empty_list_for_empty_ids(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        board = Board([white])

        result = board.get_circles_by_ids([])

        assert result == []

    def test_returns_empty_list_when_no_ids_match(self):
        white = Circle(CircleCoords(5, 5), CircleTeam.White)
        black = Circle(CircleCoords(4, 6), CircleTeam.Black)
        board = Board([white, black])

        result = board.get_circles_by_ids([uuid4(), uuid4()])

        assert result == []

    def test_ignores_new_ids_from_circles_not_on_board(self):
        board_white = Circle(CircleCoords(5, 5), CircleTeam.White)
        board_black = Circle(CircleCoords(4, 6), CircleTeam.Black)
        board = Board([board_white, board_black])

        external_white_same_coords = Circle(CircleCoords(5, 5), CircleTeam.White)
        external_black_same_coords = Circle(CircleCoords(4, 6), CircleTeam.Black)

        result = board.get_circles_by_ids([
            external_white_same_coords.circle_id,
            external_black_same_coords.circle_id,
        ])

        assert external_white_same_coords.circle_id != board_white.circle_id
        assert external_black_same_coords.circle_id != board_black.circle_id
        assert result == []