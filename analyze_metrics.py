#!/usr/bin/env python3
"""
Анализ метрик обучения из JSON файла.
Использование: python3 analyze_metrics.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

def load_metrics(filepath: str = None) -> Dict:
    """Загрузить метрики из JSON файла.
    
    Если filepath не указан, автоматически находит самый свежий файл metrics_*.json
    """
    metrics_dir = Path("./metrics")
    
    # Если filepath указан явно, используем его
    if filepath:
        path = Path(filepath)
    else:
        # Ищем самый свежий файл metrics_*.json
        if not metrics_dir.exists():
            print(f"❌ Папка {metrics_dir} не найдена")
            sys.exit(1)
        
        metrics_files = sorted(metrics_dir.glob("metrics_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not metrics_files:
            print(f"❌ Файлы метрик не найдены в {metrics_dir}")
            sys.exit(1)
        
        path = metrics_files[0]
        print(f"📂 Загружаю метрики из: {path.name}")
    
    if not path.exists():
        print(f"❌ Файл {path} не найден")
        sys.exit(1)
    
    with open(path) as f:
        return json.load(f)

def print_summary(data: Dict):
    """Вывести общую сводку."""
    iterations = data.get('iterations', [])
    if not iterations:
        print("❌ Нет данных о итерациях")
        return
    
    print("\n" + "="*80)
    print("📊 ОБЩАЯ СВОДКА")
    print("="*80)
    
    total_games = sum(it['num_episodes'] for it in iterations)
    total_white_wins = sum(it['wins_white'] for it in iterations)
    total_black_wins = sum(it['wins_black'] for it in iterations)
    total_draws = sum(it['draws'] for it in iterations)
    
    print(f"\n🎮 Всего итераций: {len(iterations)}")
    print(f"🎮 Всего игр: {total_games}")
    print(f"   • Побед белых: {total_white_wins} ({total_white_wins/total_games*100:.1f}%)")
    print(f"   • Побед черных: {total_black_wins} ({total_black_wins/total_games*100:.1f}%)")
    print(f"   • Ничьих: {total_draws} ({total_draws/total_games*100:.1f}%)")
    
    avg_moves = sum(it['avg_moves_per_game'] for it in iterations) / len(iterations)
    print(f"\n⏱️  Среднее количество ходов: {avg_moves:.1f}")
    print(f"   • Минимум за всё время: {min(it['min_moves'] for it in iterations)}")
    print(f"   • Максимум за всё время: {max(it['max_moves'] for it in iterations)}")
    
    avg_loss = sum(it['train_loss'] for it in iterations if it['train_loss'] > 0) / len([it for it in iterations if it['train_loss'] > 0])
    print(f"\n🧠 Средний Loss: {avg_loss:.4f}")
    print(f"   • Первая итерация: {iterations[0]['train_loss']:.4f}")
    print(f"   • Последняя итерация: {iterations[-1]['train_loss']:.4f}")
    
    accepted_models = sum(1 for it in iterations if it['model_accepted'])
    print(f"\n✅ Принято моделей: {accepted_models}/{len(iterations)}")
    
    print("\n" + "="*80)

def print_iteration_details(data: Dict):
    """Вывести детали каждой итерации."""
    iterations = data.get('iterations', [])
    
    print("\n" + "="*80)
    print("📈 ДЕТАЛИ ПО ИТЕРАЦИЯМ")
    print("="*80)
    
    print(f"\n{'Ит':<4} {'Ходов':<8} {'⚪':<6} {'⚫':<6} {'🤝':<6} {'Loss':<8} {'Статус':<12}")
    print("-" * 80)
    
    for it in iterations:
        status = "✅ Принята" if it['model_accepted'] else "❌ Отклон"
        print(f"{it['iteration']:<4} "
              f"{it['avg_moves_per_game']:<8.1f} "
              f"{it['wins_white']:<6} "
              f"{it['wins_black']:<6} "
              f"{it['draws']:<6} "
              f"{it['train_loss']:<8.4f} "
              f"{status:<12}")
    
    print("="*80)

def print_trends(data: Dict):
    """Вывести тренды."""
    iterations = data.get('iterations', [])
    if len(iterations) < 2:
        print("⚠️  Нужно минимум 2 итерации для анализа трендов")
        return
    
    print("\n" + "="*80)
    print("📉 ТРЕНДЫ")
    print("="*80)
    
    # Тренд ходов
    first_moves = iterations[0]['avg_moves_per_game']
    last_moves = iterations[-1]['avg_moves_per_game']
    moves_trend = "📈 растет" if last_moves > first_moves else "📉 падает"
    print(f"\n⏱️  Количество ходов: {moves_trend}")
    print(f"   • Было: {first_moves:.1f} → Стало: {last_moves:.1f}")
    
    # Тренд loss
    first_loss = iterations[0]['train_loss']
    last_loss = iterations[-1]['train_loss']
    if first_loss > 0 and last_loss > 0:
        loss_trend = "📉 улучшается" if last_loss < first_loss else "📈 ухудшается"
        print(f"\n🧠 Loss: {loss_trend}")
        print(f"   • Было: {first_loss:.4f} → Стало: {last_loss:.4f}")
    
    # Тренд побед нов. модели
    new_wins_trend = []
    for it in iterations[-min(3, len(iterations)):]:
        if it['arena_new_wins'] + it['arena_prev_wins'] > 0:
            pct = it['arena_new_wins'] / (it['arena_new_wins'] + it['arena_prev_wins']) * 100
            new_wins_trend.append(pct)
    
    if new_wins_trend:
        print(f"\n⚔️  Побеков новой модели в арене:")
        for i, pct in enumerate(new_wins_trend[-3:]):
            print(f"   • Итерация {len(iterations) - 2 + i}: {pct:.1f}%")
    
    print("\n" + "="*80)

def main():
    data = load_metrics()
    
    print("\n🎮 Анализ метрик Abalon обучения")
    
    print_summary(data)
    print_iteration_details(data)
    print_trends(data)
    
    print("\n💡 Советы для анализа:")
    print("   • Если Loss не падает → нужно менять гиперпараметры")
    print("   • Если ходов становится больше → бот не находит выигрыш")
    print("   • Если новая модель проигрывает → старая лучше, модель не сходится")
    print("   • Ищите долгосрочные тренды, а не отдельные выбросы")

if __name__ == '__main__':
    main()
