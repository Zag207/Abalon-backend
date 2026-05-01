from ast import Tuple
from enum import Enum
import logging

import numpy as np

from aiBot.game_state_utils import get_team_code
from core.board.circle_team import CircleTeam

from .game_ai_state import NumpyAbalonGameState

log = logging.getLogger(__name__)


WINNER_SCORE = 6
MAX_MOVES = 200  # Ограничение в 200 ходов суммарно
MOVES_LIMIT_VALUE = 0.8  # Value при завершении по лимиту ходов

class GameEndStatus(Enum):
    NotEnded = 'not_ended'
    ScoreWin = 'score_win'
    MovesLimit = 'moves_limit'

def is_win(game_state: NumpyAbalonGameState) -> bool:
    return 14 - int(np.count_nonzero(game_state.board == -1)) >= WINNER_SCORE or \
           14 - int(np.count_nonzero(game_state.board == 1)) >= WINNER_SCORE

def is_moves_limit_reached(game_state: NumpyAbalonGameState) -> bool:
    """Проверяет, достигнут ли лимит в 200 ходов БЕЗ ИЗМЕНЕНИЯ СЧЕТА."""

    # Если счет не менялся с начала (last_score_change_move = 0) и уже 200 ходов
    # ИЛИ если с последнего изменения счета прошло 200 ходов
    moves_since_last_score = game_state.move_count - game_state.last_score_change_move
    
    result = game_state.move_count >= MAX_MOVES and moves_since_last_score >= MAX_MOVES
    
    if game_state.move_count > 190:  # Логируем в конце игры
        log.debug(f"[MOVES_LIMIT] move_count={game_state.move_count}, last_score_change={game_state.last_score_change_move}, since_last_score={moves_since_last_score}, result={result}")
    
    return result

def get_game_end_status(game_state: NumpyAbalonGameState) -> GameEndStatus:
    """Определяет статус окончания игры."""
    if is_win(game_state):
        return GameEndStatus.ScoreWin
    if is_moves_limit_reached(game_state):
        return GameEndStatus.MovesLimit
    return GameEndStatus.NotEnded

def get_circles_count_cross_center_line(game_state: NumpyAbalonGameState, team: CircleTeam) -> int:
    """Подсчитывает количество фишек команды, находящихся за центральной линией на вражеской территории."""
    
    # Центральная линия - это 5-я строка (индекс 4)
    # Black: -1, находятся на вражеской (белой) территории в строках 1-5 (индексы 0-4)
    # White: 1, находятся на вражеской (чёрной) территории в строках 5-9 (индексы 4-8)
    
    match team:
        case CircleTeam.Black:
            # Чёрные фишки (-1) на белой территории (строки 0-4)
            return int(np.count_nonzero(game_state.board[:4, :] == -1))
        case CircleTeam.White:
            # Белые фишки (1) на чёрной территории (строки 4-8)
            return int(np.count_nonzero(game_state.board[5:9, :] == 1))
        case _:
            raise ValueError(f"Unknown team: {team}")

def get_circles_count_on_center_line(game_state: NumpyAbalonGameState, team: CircleTeam) -> int:
    """Подсчитывает количество фишек команды, находящихся на центральной линии (5-я строка)."""
    
    # Центральная линия - это 5-я строка (индекс 4)
    # Чёрные фишки (-1) и белые фишки (1) на центральной линии
    match team:
        case CircleTeam.Black:
            return int(np.count_nonzero(game_state.board[4, :] == -1))
        case CircleTeam.White:
            return int(np.count_nonzero(game_state.board[4, :] == 1))
        case _:
            raise ValueError(f"Unknown team: {team}")

def get_winner_team(game_state: NumpyAbalonGameState) -> CircleTeam | None:
    """Определяет, какая команда выиграла традиционным способом (набрано 6 очков)."""
    
    if game_state.score_black >= WINNER_SCORE:
        return CircleTeam.Black
    elif game_state.score_white >= WINNER_SCORE:
        return CircleTeam.White
    else:
        return None

def get_team_move_reached_value(game_state: NumpyAbalonGameState, player: CircleTeam) -> float:
    """
    Возвращает value для игрока при достижении лимита ходов, сравнивая очки и количество фишек за центральной линией.
    - 0.8/-0.8: победа при лимите в 200 ходов
    - 0.0: ничья при лимите ходов
    """
    
    cross_center_count_black = get_circles_count_cross_center_line(game_state, CircleTeam.Black)
    cross_center_count_white = get_circles_count_cross_center_line(game_state, CircleTeam.White)

    count_on_center_black = 0 #get_circles_count_on_center_line(game_state, CircleTeam.Black)
    count_on_center_white = 0 #get_circles_count_on_center_line(game_state, CircleTeam.White)

    match player:
        case CircleTeam.Black:
            if game_state.score_black > game_state.score_white or \
               cross_center_count_black > cross_center_count_white or \
               count_on_center_black > count_on_center_white:
                return 0.8
            elif game_state.score_black < game_state.score_white or \
                 cross_center_count_black < cross_center_count_white or \
                 count_on_center_black < count_on_center_white:
                return -0.8
            else:
                return 0.0
        case CircleTeam.White:
            if game_state.score_black < game_state.score_white or \
               cross_center_count_black < cross_center_count_white or \
               count_on_center_black < count_on_center_white:
                return 0.8
            elif game_state.score_black > game_state.score_white or \
                 cross_center_count_black > cross_center_count_white or \
                 count_on_center_black > count_on_center_white:
                return -0.8
            else:
                return 0.0

def get_value_winner_team(game_state: NumpyAbalonGameState, player: CircleTeam, winner: CircleTeam) -> float:
    """
    Возвращает value (выиграл - 1.0, проиграл - -1.0) для игрока в зависимости от того, выиграл он или проиграл традиционным способом (6 очков).
    """
    
    if player == winner:
        return 1.0
    else:
        return -1.0

def get_value_for_player(game_state: NumpyAbalonGameState, player_team: CircleTeam) -> float | None:
    """
    Возвращает value для указанного игрока в зависимости от типа окончания игры.

    Возвращает:
    - None: если игра еще не закончилась
    - 1.0/-1.0: традиционная победа (набрано 6 очков)
    - 0.8/-0.8: победа при лимите в 200 ходов
    - 0.0: ничья при лимите ходов (одинаковый счет)
    """
    game_status = get_game_end_status(game_state)
    
    if game_status != GameEndStatus.NotEnded and game_state.move_count > 190:
        log.debug(f"[GET_VALUE] move_count={game_state.move_count}, status={game_status}, team={player_team}")

    match game_status:
        case GameEndStatus.NotEnded:
            return None
        case GameEndStatus.ScoreWin:
            return get_value_winner_team(game_state, player_team, get_winner_team(game_state)) # type: ignore
        case GameEndStatus.MovesLimit:
            return get_team_move_reached_value(game_state, player_team)
        case _:
            raise ValueError(f"Unknown game status: {game_status}")

