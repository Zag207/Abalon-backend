from copy import copy, deepcopy
from dataclasses import dataclass
from typing import List

from core.board.board import Board
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.geometry.circle_coords import CircleCoords
from core.geometry.delta_coords import DeltaCoords
from core.movement.moving_directions import MovingDirections

@dataclass(frozen=True)
class ActionMove:
    selected_coords: List[CircleCoords]
    direction: MovingDirections

circle_team = CircleTeam.White

class ActionSpace:
    _action_space: List[ActionMove]
    _action_space_len: int

    def __init__(self):
        self._action_space = ActionSpace._gen_action_space()
        self._action_space_len = len(self._action_space)
    
    @property
    def action_space(self) -> List[ActionMove]:
        if len(self._action_space) == 0:
            self._action_space = ActionSpace._gen_action_space()
        
        return self._action_space
    
    @property
    def actions_count(self) -> int:
        if self._action_space_len == 0:
            if self._action_space == []:
                self._action_space = ActionSpace._gen_action_space()

            self._action_space_len = len(self._action_space)
        
        return self._action_space_len

    @staticmethod
    def _gen_action_space() -> List[ActionMove]:
        """
        Генерирует все не выходящие за пределы доски действия в формате:
        (координаты выделенных фишек, направление движения).
        """

        action_space = []

        for line in range(9, 0, -1):
            diagonal_limits = Board.get_diagonal_limits_for_line(line)

            for diagonal in range(diagonal_limits.diagonal_start, diagonal_limits.diagonal_end + 1):
                coords1 = CircleCoords(line, diagonal)
                circle = Circle(coords1, CircleTeam.White)

                action_space.extend(ActionSpace._gen_moves_with_directions([circle]))
                action_space.extend(ActionSpace._gen_parall_moves_for_line(coords1))

        return action_space

    @staticmethod
    def _gen_parall_moves_for_line(coords_first: CircleCoords) -> List[ActionMove]:
        """
        Генерирует все параллельные ходы для текущей линии в направлениях Right, UpRight, UpLeft
        """

        actions = []
        circle = Circle(coords_first, circle_team)

        actions.extend(ActionSpace._gen_parall_moves_in_direction(circle, MovingDirections.Right))
        actions.extend(ActionSpace._gen_parall_moves_in_direction(circle, MovingDirections.UpRight))
        actions.extend(ActionSpace._gen_parall_moves_in_direction(circle, MovingDirections.UpLeft))

        return actions

    @staticmethod
    def _gen_parall_moves_in_direction(circle_first: Circle, line_dir: MovingDirections) -> List[ActionMove]:
        """
        Генерирует параллельные ходы в определённом направлении с добавлением фигур до 3 штук в линии
        """

        actions = []
        circles = [circle_first]
        delta_coords = DeltaCoords.get_delta_coords_from_moving(line_dir)

        actions.extend(ActionSpace._extend_circle_line_for_parall(circles, delta_coords))
        actions.extend(ActionSpace._extend_circle_line_for_parall(circles, delta_coords))

        return actions
    
    @staticmethod
    def _extend_circle_line_for_parall(
        circles: List[Circle],
        delta_coords: DeltaCoords
        ) -> List[ActionMove]:
        """
        Добавляет к линии ещё одну фишку и генерирует для неё ходы
        """

        actions = []
        coords = circles[-1].coords.get_new_coords(delta_coords)

        if not Board.is_in_board(coords):
            return actions

        circles.append(Circle(coords, circle_team))
        actions.extend(ActionSpace._gen_moves_with_directions(circles))

        return actions

    @staticmethod
    def _gen_moves_with_directions(circles_checked: List[Circle]) -> List[ActionMove]:
        """
        Генерирует ходы для всех направлений для выбранных фишек
        """

        actions = []

        # Можно оптимизировать, если не проверять направления, вдоль которых расположена линия
        
        for moving in MovingDirections:
            if moving == MovingDirections.NoMove:
                continue
            
            circles_checked_copy = deepcopy(circles_checked)
            board = Board(circles_checked_copy)
            moving_res = board.move([circle.circle_id for circle in circles_checked_copy], moving, circle_team)

            if not moving_res.is_error:
                actions.append(ActionMove([copy(circle.coords) for circle in circles_checked], moving))
        
        return actions

