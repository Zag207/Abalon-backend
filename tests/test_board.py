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