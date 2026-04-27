# Как менять параметры игры

## Основные параметры игры

Все основные параметры находятся в [src/core/game_state.py](src/core/game_state.py#L12-L14):

```python
WINNER_SCORE = 6              # Победа при количестве очков
MAX_MOVES = 200               # Лимит ходов без набора очков
MOVES_LIMIT_VALUE = 0.8       # Value при победе по лимиту (вместо ±1.0)
```

**Изменяем так:**
- `WINNER_SCORE = 5` → победа при 5 очках вместо 6
- `MAX_MOVES = 300` → 300 ходов без изменения счета вместо 200
- `MOVES_LIMIT_VALUE = 0.5` → меньше мотивации на активную игру

## Параметры обучения

Находятся в [src/aiBot/train_bot.py](src/aiBot/train_bot.py):

| Параметр | Где | Значение | Что делает |
|----------|-----|---------|-----------|
| `numIters` | train_bot.py | 10 | Сколько итераций обучения |
| `numEps` | train_bot.py | 20 | Эпизодов самоигры в итерацию |
| `tempThreshold` | train_bot.py | 15 | После какого хода temp=0 |
| `arenaCompare` | train_bot.py | 40 | Игр для сравнения моделей |
| `updateThreshold` | train_bot.py | 0.55 | % побед для принятия модели |
| `maxlenOfQueue` | train_bot.py | 200000 | Размер очереди примеров |

**Пример изменения:**
```python
args = Args(
    numIters=50,              # Больше итераций = дольше обучение
    numEps=50,                # Больше эпизодов = лучше обучение
    tempThreshold=10,         # Раньше переходить на greedy
    arenaCompare=100,         # Более тщательное сравнение
    updateThreshold=0.6,      # Более строгий критерий
)
```

## Параметры нейросети

Находятся в [src/aiBot/neural_net.py](src/aiBot/neural_net.py#L24-L25):

```python
def __init__(self, action_size: int, num_resblocks: int = 6, channels: int = 64):
```

**Изменяем так:**
- `num_resblocks=6` → 3 (быстрее, но менее мощная) или 10 (мощнее, но медленнее)
- `channels=64` → 32 (экономнее) или 128 (мощнее)

## Параметры MCTS

Находятся в [src/aiBot/base_alpha_zero/MCTS.py](src/aiBot/base_alpha_zero/MCTS.py):

```python
num_simulations = 25  # Строка ~20
```

Увеличение улучшает качество, но замедляет процесс:
- `25` → `50` (точнее, медленнее)
- `25` → `10` (быстрее, менее точно)

## Быстрый чек-лист для экспериментов

### Хочу быстро протестировать:
```
WINNER_SCORE = 3          # Короче игра
MAX_MOVES = 100           # Меньше ходов
numIters = 2              # Минимум итераций
numEps = 5                # Мало эпизодов
arenaCompare = 10         # Мало игр
num_resblocks = 3         # Меньше слоев
```

### Хочу лучшего качества:
```
WINNER_SCORE = 6          # Стандарт
MAX_MOVES = 200           # Стандарт
numIters = 100            # Много итераций
numEps = 100              # Много эпизодов
arenaCompare = 100        # Тщательное тестирование
num_resblocks = 10        # Мощная сеть
channels = 128            # Больше параметров
```

### Хочу сбалансировать:
```
WINNER_SCORE = 6          # Стандарт
MAX_MOVES = 200           # Стандарт
numIters = 30             # Среднее количество
numEps = 30               # Среднее количество
arenaCompare = 50         # Хорошее тестирование
num_resblocks = 6         # Стандарт
```

## Как проверить текущие параметры?

Посмотрите логи при запуске:
```bash
cd /home/zag207/Abalon-backend
uv run ./src/aiBot/train_bot.py 2>&1 | head -100
```

Там будут видны все параметры и их значения.

## Сохранение конфигов

Рекомендуемая структура для хранения конфигов:
```
configs/
  - default.yaml
  - fast_test.yaml
  - high_quality.yaml
  - custom.yaml
```

Но сейчас они хардкодированы, поэтому просто меняйте в исходных файлах перед запуском.
