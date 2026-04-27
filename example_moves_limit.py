#!/usr/bin/env python3
"""
Пример использования нового функционала с лимитом ходов и value при окончании игры.
"""

from src.core.game_state import GameState, MAX_MOVES, MOVES_LIMIT_VALUE
from src.core.setup.prepare_circles import fill_circle_board
from src.core.board.circle_team import CircleTeam


def example_check_game_status():
    """Демонстрирует проверку статуса игры."""
    game_state = GameState(fill_circle_board())
    
    # Пока игра не закончилась
    print(f"Игра закончилась: {game_state.is_game_ended()}")  # False
    print(f"Тип окончания: {game_state.get_game_end_type()}")  # 'not_ended'
    print(f"Счетчик ходов: {game_state.move_count}")  # 0
    print(f"Последний ход со счетом: {game_state.last_score_change_move}")  # 0
    
    # Value для каждого игрока, когда игра не закончилась
    print(f"Value для Black: {game_state.get_value_for_player(CircleTeam.Black)}")  # None
    print(f"Value для White: {game_state.get_value_for_player(CircleTeam.White)}")  # None


def example_moves_limit_victory():
    """Демонстрирует победу по количеству ходов."""
    game_state = GameState(fill_circle_board())
    
    # Имитируем 200 ходов без изменения счета
    game_state.move_count = 200
    game_state.last_score_change_move = 0  # Счет не менялся с начала
    game_state.score_black = 3
    game_state.score_white = 1
    
    print(f"\nПосле {game_state.move_count} ходов:")
    print(f"Игра закончилась: {game_state.is_game_ended()}")  # True
    print(f"Тип окончания: {game_state.get_game_end_type()}")  # 'moves_limit'
    print(f"Черные: {game_state.score_black}, Белые: {game_state.score_white}")
    
    # Value = ±0.8 (не ±1.0, чтобы мотивировать активную игру)
    print(f"Value для Black (выигрывает): {game_state.get_value_for_player(CircleTeam.Black)}")  # 0.8
    print(f"Value для White (проигрывает): {game_state.get_value_for_player(CircleTeam.White)}")  # -0.8


def example_traditional_victory():
    """Демонстрирует традиционную победу (6 очков)."""
    game_state = GameState(fill_circle_board())
    
    game_state.score_black = 6
    game_state.move_count = 50
    
    print(f"\nТрадиционная победа (6 очков):")
    print(f"Игра закончилась: {game_state.is_game_ended()}")  # True
    print(f"Тип окончания: {game_state.get_game_end_type()}")  # 'score_win'
    
    # Value = ±1.0 (полная награда)
    print(f"Value для Black (выигрывает): {game_state.get_value_for_player(CircleTeam.Black)}")  # 1.0
    print(f"Value для White (проигрывает): {game_state.get_value_for_player(CircleTeam.White)}")  # -1.0


def example_draw_at_moves_limit():
    """Демонстрирует ничью при лимите ходов."""
    game_state = GameState(fill_circle_board())
    
    game_state.move_count = 200
    game_state.last_score_change_move = 0
    game_state.score_black = 2
    game_state.score_white = 2  # Одинаковый счет = ничья
    
    print(f"\nНичья при лимите ходов:")
    print(f"Черные: {game_state.score_black}, Белые: {game_state.score_white}")
    print(f"Тип окончания: {game_state.get_game_end_type()}")  # 'moves_limit'
    
    # Value = 0.0 для обоих (ничья)
    print(f"Value для Black: {game_state.get_value_for_player(CircleTeam.Black)}")  # 0.0
    print(f"Value для White: {game_state.get_value_for_player(CircleTeam.White)}")  # 0.0


if __name__ == '__main__':
    print("=" * 60)
    print("Примеры использования лимита ходов и value при окончании")
    print("=" * 60)
    
    example_check_game_status()
    example_moves_limit_victory()
    example_traditional_victory()
    example_draw_at_moves_limit()
    
    print("\n" + "=" * 60)
    print(f"Таблица значений Value:")
    print("=" * 60)
    print(f"{'Сценарий':<40} | {'Black':<7} | {'White':<7}")
    print("-" * 60)
    print(f"{'Игра не закончилась':<40} | {None:<7} | {None:<7}")
    print(f"{'Black набрал 6 очков':<40} | {1.0:<7} | {-1.0:<7}")
    print(f"{'White набрал 6 очков':<40} | {-1.0:<7} | {1.0:<7}")
    print(f"{'200 ходов, Black выигрывает':<40} | {0.8:<7} | {-0.8:<7}")
    print(f"{'200 ходов, ничья':<40} | {0.0:<7} | {0.0:<7}")
    print("=" * 60)
