from aiBot.game_state_utils import get_matrix_from_board
from aiBot.numpy_game_logic.game_ai_state import NumpyAbalonGameState
from core.game_state import GameState


class GameStateConverter:
    @staticmethod
    def to_numpy_game_state(game_state: GameState) -> NumpyAbalonGameState:
        matrix_board = get_matrix_from_board(game_state.board)

        return NumpyAbalonGameState(
            board=matrix_board,
            score_black=game_state.score_black,
            score_white=game_state.score_white,
            move_count=game_state.move_count,
            last_score_change_move=game_state.last_score_change_move
        )
    