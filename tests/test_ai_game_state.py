from copy import deepcopy

import numpy as np
import pytest

from aiBot.AbalonAiGameState import AbalonAiGameState
from core.board.circle_team import CircleTeam
from core.game_state import GameState


def _count_team_circles(state: GameState, team: CircleTeam) -> int:
    return sum(1 for circle in state.board.circles if circle.circle_type == team)


def test_get_init_board_returns_game_state_with_expected_piece_counts():
    game = AbalonAiGameState()

    board = game.getInitBoard()

    assert isinstance(board, GameState)
    assert len(board.board.circles) == 28
    assert _count_team_circles(board, CircleTeam.White) == 14
    assert _count_team_circles(board, CircleTeam.Black) == 14


def test_get_board_size_and_action_size_are_valid():
    game = AbalonAiGameState()

    assert game.getBoardSize() == (9, 9)
    assert game.getActionSize() > 0


def test_get_game_ended_is_none_on_initial_position():
    game = AbalonAiGameState()
    board = game.getInitBoard()

    assert game.getGameEnded(board, 1) is None


def test_get_canonical_form_for_white_returns_equivalent_copy():
    game = AbalonAiGameState()
    board = game.getInitBoard()

    canonical = game.getCanonicalForm(board, 1)

    assert canonical is not board
    assert game.stringRepresentation(canonical) == game.stringRepresentation(board)


def test_get_canonical_form_for_black_swaps_colors():
    game = AbalonAiGameState()
    board = game.getInitBoard()

    canonical = game.getCanonicalForm(board, -1)

    assert _count_team_circles(canonical, CircleTeam.White) == _count_team_circles(board, CircleTeam.Black)
    assert _count_team_circles(canonical, CircleTeam.Black) == _count_team_circles(board, CircleTeam.White)


def test_get_valid_moves_returns_binary_int8_mask():
    game = AbalonAiGameState()
    board = game.getInitBoard()

    valids = game.getValidMoves(board, 1)

    assert valids.shape == (game.getActionSize(),)
    assert valids.dtype == np.int8
    assert np.all(np.isin(valids, [0, 1]))
    assert int(np.sum(valids)) > 0


def test_get_next_state_returns_new_state_and_flips_player_without_mutating_input():
    game = AbalonAiGameState()
    board = game.getInitBoard()
    board_before = game.stringRepresentation(board)

    valids = game.getValidMoves(board, 1)
    action = int(np.argmax(valids))
    assert valids[action] == 1

    next_state, next_player = game.getNextState(board, 1, action)

    assert next_state is not board
    assert next_player == -1
    assert game.stringRepresentation(board) == board_before


def test_string_representation_is_deterministic_for_equivalent_states():
    game = AbalonAiGameState()
    board = game.getInitBoard()
    board_copy = deepcopy(board)

    assert game.stringRepresentation(board) == game.stringRepresentation(board_copy)


def test_get_symmetries_raises_on_policy_size_mismatch():
    game = AbalonAiGameState()
    board = game.getInitBoard()
    bad_pi = np.zeros(game.getActionSize() - 1, dtype=np.float32)

    with pytest.raises(ValueError):
        game.getSymmetries(board, bad_pi)
