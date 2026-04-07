from core.board.board import MoveResult
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.game_state import GameState, WINNER_SCORE
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections


class TestGameState:
	def test_init_sets_default_state(self):
		circles = [Circle(CircleCoords(5, 5), CircleTeam.White)]

		state = GameState(circles)

		assert state.curr_team == CircleTeam.White
		assert state.score_black == 0
		assert state.score_white == 0
		assert state.board.circles == circles

	def test_get_winner_team_returns_none_when_no_winner(self):
		state = GameState([])

		assert state.get_winner_team() is None

	def test_get_winner_team_returns_black_at_threshold(self):
		state = GameState([])
		state.score_black = WINNER_SCORE

		assert state.get_winner_team() == CircleTeam.Black

	def test_get_winner_team_returns_white_above_threshold(self):
		state = GameState([])
		state.score_white = WINNER_SCORE + 1

		assert state.get_winner_team() == CircleTeam.White

	def test_is_win_returns_true_when_any_score_reaches_threshold(self):
		state = GameState([])
		state.score_white = WINNER_SCORE

		assert state.is_win() is True

	def test_get_moving_team_returns_enemy_of_current_team(self):
		state = GameState([])
		state.curr_team = CircleTeam.Black

		assert state.get_moving_team() == CircleTeam.White

	def test_get_circles_returns_board_circles(self):
		circles = [Circle(CircleCoords(5, 5), CircleTeam.White)]
		state = GameState(circles)

		assert state.get_circles() == circles

	def test_move_returns_error_if_moving_team_not_expected(self, monkeypatch):
		state = GameState([])

		def fail_if_called(*_args, **_kwargs):
			raise AssertionError("board.move should not be called")

		monkeypatch.setattr(state.board, "move", fail_if_called)

		res = state.move([], MovingDirections.Right, CircleTeam.White)

		assert res.is_error is True
		assert res.circles_moving == []
		assert state.curr_team == CircleTeam.White

	def test_move_updates_turn_and_black_score_on_success(self, monkeypatch):
		state = GameState([])
		moved = [Circle(CircleCoords(5, 5), CircleTeam.Black)]

		monkeypatch.setattr(
			state.board,
			"move",
			lambda *_args, **_kwargs: MoveResult(
				is_error=False,
				increasing_score=1,
				circles_moving=moved,
			),
		)

		res = state.move([], MovingDirections.Right, CircleTeam.Black)

		assert res.is_error is False
		assert res.circles_moving == moved
		assert state.curr_team == CircleTeam.Black
		assert state.score_black == 1
		assert state.score_white == 0

	def test_move_updates_white_score_on_success(self, monkeypatch):
		state = GameState([])
		state.curr_team = CircleTeam.Black

		monkeypatch.setattr(
			state.board,
			"move",
			lambda *_args, **_kwargs: MoveResult(
				is_error=False,
				increasing_score=1,
				circles_moving=[],
			),
		)

		res = state.move([], MovingDirections.Left, CircleTeam.White)

		assert res.is_error is False
		assert state.curr_team == CircleTeam.White
		assert state.score_white == 1
		assert state.score_black == 0

	def test_move_does_not_change_state_when_board_returns_error(self, monkeypatch):
		state = GameState([])

		monkeypatch.setattr(
			state.board,
			"move",
			lambda *_args, **_kwargs: MoveResult(is_error=True),
		)

		res = state.move([], MovingDirections.Right, CircleTeam.Black)

		assert res.is_error is True
		assert state.curr_team == CircleTeam.White
		assert state.score_black == 0
		assert state.score_white == 0

	def test_move_does_not_increase_score_when_increasing_score_is_zero(self, monkeypatch):
		state = GameState([])

		monkeypatch.setattr(
			state.board,
			"move",
			lambda *_args, **_kwargs: MoveResult(
				is_error=False,
				increasing_score=0,
				circles_moving=[],
			),
		)

		res = state.move([], MovingDirections.Right, CircleTeam.Black)

		assert res.is_error is False
		assert state.curr_team == CircleTeam.Black
		assert state.score_black == 0
		assert state.score_white == 0
