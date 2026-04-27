"""
Сбор и логирование метрик обучения.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List

log = logging.getLogger(__name__)


@dataclass
class GameMetrics:
    """Метрики одной партии."""
    episode_num: int
    move_count: int  # Количество ходов
    white_score: int
    black_score: int
    end_type: str  # 'score_win' или 'moves_limit'
    winner: str  # 'White', 'Black', 'Draw'
    value: float  # ±1.0, ±0.8, или 0.0


@dataclass
class IterationMetrics:
    """Агрегированные метрики за одну итерацию обучения."""
    iteration: int
    num_episodes: int
    
    # Ходы
    avg_moves_per_game: float = 0.0
    min_moves: int = 0
    max_moves: int = 0
    
    # Результаты
    wins_white: int = 0
    wins_black: int = 0
    draws: int = 0
    wins_by_score: int = 0
    wins_by_moves_limit: int = 0
    
    # Счет
    avg_white_score: float = 0.0
    avg_black_score: float = 0.0
    
    # Обучение
    train_loss: float = 0.0
    arena_new_wins: int = 0
    arena_prev_wins: int = 0
    arena_draws: int = 0
    model_accepted: bool = False
    
    # Временные
    games: List[GameMetrics] = field(default_factory=list)


class MetricsCollector:
    """Сборщик метрик обучения."""
    
    def __init__(self, output_dir: str = "./metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Создаем файл с временной меткой для каждого запуска
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.metrics_file = self.output_dir / f'metrics_{timestamp}.json'
        
        self.iterations: List[IterationMetrics] = []
        self.current_iteration: IterationMetrics | None = None
    
    def start_iteration(self, iteration: int, num_episodes: int):
        """Начало новой итерации."""
        self.current_iteration = IterationMetrics(iteration=iteration, num_episodes=num_episodes)
    
    def add_game(self, episode_num: int, move_count: int, white_score: int, 
                 black_score: int, end_type: str, winner: str, value: float):
        """Добавить метрики игры."""
        if self.current_iteration is None:
            raise RuntimeError("Итерация не начата")
        
        game = GameMetrics(
            episode_num=episode_num,
            move_count=move_count,
            white_score=white_score,
            black_score=black_score,
            end_type=end_type,
            winner=winner,
            value=value,
        )
        self.current_iteration.games.append(game)
    
    def finalize_iteration(self, train_loss: float = 0.0, 
                          arena_new: tuple = (0, 0, 0),
                          model_accepted: bool = False):
        """Завершить итерацию и вычислить агрегированные метрики."""
        if self.current_iteration is None:
            raise RuntimeError("Итерация не начата")
        
        games = self.current_iteration.games
        if not games:
            log.warning("Нет игр в итерации")
            return
        
        # Ходы
        move_counts = [g.move_count for g in games]
        self.current_iteration.avg_moves_per_game = sum(move_counts) / len(move_counts)
        self.current_iteration.min_moves = min(move_counts)
        self.current_iteration.max_moves = max(move_counts)
        
        # Результаты
        for game in games:
            if game.winner == "White":
                self.current_iteration.wins_white += 1
            elif game.winner == "Black":
                self.current_iteration.wins_black += 1
            elif game.winner == "Draw":
                self.current_iteration.draws += 1
            
            if game.end_type == "score_win":
                self.current_iteration.wins_by_score += 1
            elif game.end_type == "moves_limit":
                self.current_iteration.wins_by_moves_limit += 1
        
        # Счет
        white_scores = [g.white_score for g in games]
        black_scores = [g.black_score for g in games]
        self.current_iteration.avg_white_score = sum(white_scores) / len(white_scores)
        self.current_iteration.avg_black_score = sum(black_scores) / len(black_scores)
        
        # Обучение
        self.current_iteration.train_loss = train_loss
        self.current_iteration.arena_new_wins, self.current_iteration.arena_prev_wins, self.current_iteration.arena_draws = arena_new
        self.current_iteration.model_accepted = model_accepted
        
        self.iterations.append(self.current_iteration)
        self._log_iteration()
        self._save_to_file()
    
    def _log_iteration(self):
        """Логировать метрики итерации."""
        it = self.current_iteration
        total_games = it.wins_white + it.wins_black + it.draws
        
        log.info("\n" + "="*80)
        log.info(f"📊 МЕТРИКИ ИТЕРАЦИИ #{it.iteration}")
        log.info("="*80)
        
        log.info(f"🎮 ИГРЫ ({it.num_episodes} эпизодов):")
        log.info(f"   • Ходов: {it.avg_moves_per_game:.1f} ± [{it.min_moves}, {it.max_moves}]")
        log.info(f"   • Результаты: ⚪ {it.wins_white} | ⚫ {it.wins_black} | 🤝 {it.draws}")
        win_pct_white = (it.wins_white / total_games * 100) if total_games > 0 else 0
        win_pct_black = (it.wins_black / total_games * 100) if total_games > 0 else 0
        log.info(f"   • Проценты: ⚪ {win_pct_white:.1f}% | ⚫ {win_pct_black:.1f}%")
        
        by_type = [
            ("По очкам (6)", it.wins_by_score),
            ("По лимиту (200)", it.wins_by_moves_limit),
        ]
        log.info(f"   • Способ выигрыша: {', '.join(f'{name}={cnt}' for name, cnt in by_type)}")
        
        log.info(f"📈 СЧЕТ:")
        log.info(f"   • Белые: {it.avg_white_score:.2f} ± очков/партию")
        log.info(f"   • Черные: {it.avg_black_score:.2f} ± очков/партию")
        
        if it.train_loss > 0:
            log.info(f"🧠 ОБУЧЕНИЕ НЕЙРОСЕТИ:")
            log.info(f"   • Loss: {it.train_loss:.4f}")
        
        if it.arena_new_wins + it.arena_prev_wins > 0:
            log.info(f"⚔️  АРЕНА (сравнение моделей):")
            log.info(f"   • Новая модель: {it.arena_new_wins} побед")
            log.info(f"   • Старая модель: {it.arena_prev_wins} побед")
            log.info(f"   • Ничьих: {it.arena_draws}")
            if it.model_accepted:
                log.info(f"   • ✅ МОДЕЛЬ ПРИНЯТА")
            else:
                log.info(f"   • ❌ Модель отклонена")
        
        log.info("="*80 + "\n")
    
    def _save_to_file(self):
        """Сохранить метрики в JSON."""
        data = {
            "iterations": [asdict(it) for it in self.iterations]
        }
        with open(self.metrics_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        log.debug(f"Метрики сохранены в {self.metrics_file}")
    
    def get_summary(self):
        """Получить сводку по всем итерациям."""
        if not self.iterations:
            return {}
        
        last_it = self.iterations[-1]
        return {
            "total_iterations": len(self.iterations),
            "last_iteration": last_it.iteration,
            "total_games": sum(it.num_episodes for it in self.iterations),
            "avg_moves": sum(it.avg_moves_per_game for it in self.iterations) / len(self.iterations),
            "white_wins": sum(it.wins_white for it in self.iterations),
            "black_wins": sum(it.wins_black for it in self.iterations),
            "draws": sum(it.draws for it in self.iterations),
        }
