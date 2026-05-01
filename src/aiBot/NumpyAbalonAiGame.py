from typing import List, Tuple

import numpy as np
import numpy.typing as npt

from core.board.circle_team import CircleTeam

from .numpy_game_logic.game_end_logic import get_value_for_player
from .numpy_game_logic.game_ai_state import NumpyAbalonGameState
from .numpy_game_logic.numpy_validation_logic import validate_action
from .numpy_game_logic.move_apply import apply_move_to_board

from .base_alpha_zero.Game import Game

from core.board.circle import Circle

from .game_state_utils import get_matrix_from_board, get_team_from_code
from core.game_state import GameState

from .action_space import ActionSpace

class NumpyAbalonAiGame(Game):
    action_space: ActionSpace

    def __init__(self):
        super().__init__()

        self.action_space = ActionSpace()
    
    def getInitBoard(self, board: GameState):
        return get_matrix_from_board(board.board)
    
    def getBoardSize(self) -> Tuple[int, int]:
        return (9, 9)
    
    def getActionSize(self) -> int:
        return self.action_space.actions_count
    
    def getCanonicalForm(self, board: NumpyAbalonGameState, player: int) -> NumpyAbalonGameState:
        if player == -1:
            # Меняем белые ↔ чёрные
            swapped_board = board.board.copy()
            mask_white = board.board == 1
            mask_black = board.board == -1
            swapped_board[mask_white] = -1
            swapped_board[mask_black] = 1
            
            # ВАЖНО: меняем и очки!
            return NumpyAbalonGameState(
                board=swapped_board,
                score_white=board.score_black,
                score_black=board.score_white,
                move_count=board.move_count,
                last_score_change_move=board.last_score_change_move
            )
        else:
            # Возвращаем копию (или тот же объект, если dataclass immutable)
            return NumpyAbalonGameState(
                board=board.board.copy(),
                score_white=board.score_white,
                score_black=board.score_black,
                move_count=board.move_count,
                last_score_change_move=board.last_score_change_move
            )
    
    def stringRepresentation(self, board: NumpyAbalonGameState) -> str:
        # Warning: Может быть баг - состояния различаются по другим полям, а не только по доске. Но для простоты пока так.

        # Преобразуем матрицу в строку для уникального представления
        return ''.join(map(str, board.board.flatten()))

    def getValidMoves(
            self, 
            board: NumpyAbalonGameState, 
            player: int
            ) -> npt.NDArray[np.int8]:
        valid_moves_mask = 0*np.ones(self.getActionSize(), dtype=np.int8)
        curr_team = get_team_from_code(player)

        for index, action in enumerate(self.action_space.action_space):
            action_coords = action.selected_coords
            circles = [Circle(coords, curr_team) for coords in action_coords]

            is_action_valid = validate_action(circles, board.board, curr_team, action.direction)

            valid_moves_mask[index] = is_action_valid

        return valid_moves_mask

    def getGameEnded(
            self, 
            board: NumpyAbalonGameState, 
            player: int
            ) -> float | None:
        """
        Возвращает value (награду) для текущего игрока если игра закончилась.
        
        Возвращает:
        - None: если игра еще не закончилась
        - 1.0: если текущий игрок выиграл традиционным способом (6 очков)
        - -1.0: если текущий игрок проиграл традиционным способом
        - 0.8: если текущий игрок выиграл по количеству очков при лимите ходов
        - -0.8: если текущий игрок проиграл по количеству очков при лимите ходов
        - 0.0: если ничья при лимите ходов (одинаковое количество очков)
        """

        curr_team = get_team_from_code(player)

        return get_value_for_player(board, curr_team)

    def getNextState(
            self, 
            board: NumpyAbalonGameState, 
            player: int, 
            action: int
            ) -> NumpyAbalonGameState:
        """
        Возвращает новое состояние игры после применения action.
        
        Args:
            board: текущее состояние доски
            player: текущий игрок (1 для White, -1 для Black)
            action: индекс действия в action_space
        
        Returns:
            новое состояние доски после хода
        """
        # Получить action из action_space
        assert 0 <= action < self.action_space.actions_count, f"Invalid action index: {action}"
        action_move = self.action_space.action_space[action]
        
        # Получить команду текущего игрока
        curr_team = get_team_from_code(player)
        player_code = player
        
        # Применить ход к доске
        move_result = apply_move_to_board(
            board.board,
            action_move.selected_coords,
            action_move.direction,
            player_code
        )
        
        # Обновить состояние
        new_board = move_result.board
        score_delta = move_result.score_delta
        
        # Обновить счёты
        new_score_black = board.score_black
        new_score_white = board.score_white
        new_last_score_change_move = board.last_score_change_move
        
        if score_delta > 0:
            match curr_team:
                case CircleTeam.White:
                    new_score_white += score_delta
                case CircleTeam.Black:
                    new_score_black += score_delta
                case _:
                    raise ValueError(f"Unknown team: {curr_team}")
            new_last_score_change_move = board.move_count
        
        # Вернуть новое состояние
        return NumpyAbalonGameState(
            board=new_board,
            score_black=new_score_black,
            score_white=new_score_white,
            move_count=board.move_count + 1,
            last_score_change_move=new_last_score_change_move
        )

    def getSymmetries(self, board: NumpyAbalonGameState, pi: npt.NDArray[np.float32]) -> List[Tuple[NumpyAbalonGameState, npt.NDArray[np.float32]]]:
        # Для простоты пока не реализуем симметрии. Можно добавить вращения и отражения доски, если будет нужно.
        return [(board, pi)]
