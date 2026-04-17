from copy import deepcopy

from aiBot.action_space import ActionSpace
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.movement.moving_directions import MovingDirections


class TestGenMovesWithDirections:
	def test_single_center_circle_has_all_six_directions(self):
		circle = Circle(CircleCoords(5, 5), CircleTeam.White)

		actions = ActionSpace._gen_moves_with_directions([circle])

		expected_directions = {
			MovingDirections.UpRight,
			MovingDirections.Right,
			MovingDirections.DownRight,
			MovingDirections.DownLeft,
			MovingDirections.Left,
			MovingDirections.UpLeft,
		}

		assert len(actions) == 6
		assert {action.direction for action in actions} == expected_directions

	def test_single_edge_circle_has_only_in_board_directions(self):
		circle = Circle(CircleCoords(1, 5), CircleTeam.White)

		actions = ActionSpace._gen_moves_with_directions([circle])

		assert {action.direction for action in actions} == {
			MovingDirections.Right,
			MovingDirections.DownRight,
			MovingDirections.DownLeft,
		}

	def test_result_never_contains_no_move(self):
		circles = [
			Circle(CircleCoords(5, 5), CircleTeam.White),
			Circle(CircleCoords(5, 6), CircleTeam.White),
		]

		actions = ActionSpace._gen_moves_with_directions(circles)

		assert all(action.direction != MovingDirections.NoMove for action in actions)

	def test_does_not_mutate_input_circles(self):
		circles = [
			Circle(CircleCoords(5, 5), CircleTeam.White),
			Circle(CircleCoords(5, 6), CircleTeam.White),
		]
		circles_before = deepcopy(circles)

		_ = ActionSpace._gen_moves_with_directions(circles)

		assert len(circles) == len(circles_before)
		assert [c.circle_id for c in circles] == [c.circle_id for c in circles_before]
		assert [(c.coords.line, c.coords.diagonal) for c in circles] == [
			(c.coords.line, c.coords.diagonal) for c in circles_before
		]

	def test_move_3_circle_group(self):
		circles = [
			Circle(CircleCoords(5, 5), CircleTeam.White),
			Circle(CircleCoords(5, 6), CircleTeam.White),
			Circle(CircleCoords(5, 7), CircleTeam.White)
		]
		
		expected_directions = {
			MovingDirections.UpRight,
			MovingDirections.DownRight,
			MovingDirections.DownLeft,
			MovingDirections.UpLeft,
		}
		
		actions = ActionSpace._gen_moves_with_directions(circles)

		assert {action.direction for action in actions} == expected_directions
