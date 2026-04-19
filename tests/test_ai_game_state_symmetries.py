import numpy as np

from aiBot.AbalonAiGameState import AbalonAiGameState
from core.board.board import Board
from core.board.circle_team import CircleTeam


def _count_team_circles(state, team: CircleTeam) -> int:
    return sum(1 for circle in state.board.circles if circle.circle_type == team)


def test_get_symmetries_returns_all_dihedral_transforms():
    game = AbalonAiGameState()
    board = game.getInitBoard()
    pi = np.zeros(game.getActionSize(), dtype=np.float32)

    symmetries = game.getSymmetries(board, pi)

    assert len(symmetries) == 12


def test_get_symmetries_preserves_policy_mass_and_shape():
    game = AbalonAiGameState()
    board = game.getInitBoard()

    pi = np.random.default_rng(42).random(game.getActionSize(), dtype=np.float32)
    pi = pi / np.sum(pi)

    symmetries = game.getSymmetries(board, pi)

    for _, transformed_pi in symmetries:
        assert transformed_pi.shape == (game.getActionSize(),)
        assert np.isclose(float(np.sum(transformed_pi)), 1.0, atol=1e-6)
        assert np.all(transformed_pi >= 0)


def test_get_symmetries_preserves_state_invariants_and_bounds():
    game = AbalonAiGameState()
    board = game.getInitBoard()
    board.curr_team = CircleTeam.Black
    board.score_white = 2
    board.score_black = 3

    pi = np.zeros(game.getActionSize(), dtype=np.float32)
    symmetries = game.getSymmetries(board, pi)

    white_count = _count_team_circles(board, CircleTeam.White)
    black_count = _count_team_circles(board, CircleTeam.Black)
    total_count = len(board.board.circles)

    for transformed_state, _ in symmetries:
        assert transformed_state.curr_team == board.curr_team
        assert transformed_state.score_white == board.score_white
        assert transformed_state.score_black == board.score_black
        assert _count_team_circles(transformed_state, CircleTeam.White) == white_count
        assert _count_team_circles(transformed_state, CircleTeam.Black) == black_count
        assert len(transformed_state.board.circles) == total_count
        assert all(Board.is_in_board(circle.coords) for circle in transformed_state.board.circles)


def test_get_symmetries_does_not_mutate_inputs():
    game = AbalonAiGameState()
    board = game.getInitBoard()
    board.curr_team = CircleTeam.Black
    board.score_white = 1
    board.score_black = 4

    pi = np.zeros(game.getActionSize(), dtype=np.float32)
    pi[0] = 0.25
    pi[10] = 0.75

    board_before = game.stringRepresentation(board)
    pi_before = pi.copy()

    _ = game.getSymmetries(board, pi)

    assert game.stringRepresentation(board) == board_before
    assert np.array_equal(pi, pi_before)
