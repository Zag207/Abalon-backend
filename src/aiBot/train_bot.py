import logging
import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime

import coloredlogs

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from base_alpha_zero.Coach import Coach
from AbalonAiGameState import AbalonAiGameState as Game
from neural_net import AbalonNNet as nn
from utils import *

log = logging.getLogger(__name__)


class ConsoleAllowListFilter(logging.Filter):
    """Allow only selected loggers (and warnings/errors) to reach console."""

    def __init__(self, allowed_logger_prefixes):
        super().__init__()
        self.allowed_logger_prefixes = tuple(allowed_logger_prefixes)

    def filter(self, record):
        if record.levelno >= logging.WARNING:
            return True
        return record.name.startswith(self.allowed_logger_prefixes)


def configure_logging():
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)

    # Создаем папку logs если её нет
    logs_dir = Path('./logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Создаем файл с временной меткой
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = logs_dir / f'app_{timestamp}.log'
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(ConsoleAllowListFilter(['__main__', 'train_bot']))
    console_handler.setFormatter(
        coloredlogs.ColoredFormatter('%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s')
    )

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


configure_logging()

DEFAULT_TRAIN_ARGS = {
    'numIters': 3,
    'numEps': 25,
    'tempThreshold': 15,
    'updateThreshold': 0.6,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 150,
    'arenaCompare': 6,
    'cpuct': 0.5,
    'checkpoint': './temp2/',
    'load_model': False,
    'load_folder_file': ('./temp2/', 'best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,
}


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Train Abalon bot with YAML config')
    parser.add_argument(
        'config',
        type=str,
        help='Path to YAML file with training parameters (for example: train_config.yaml)',
    )
    return parser.parse_args()


def load_train_args(config_file: str) -> dotdict:
    config_path = Path(config_file).expanduser().resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f'Config file not found: {config_path}')

    with config_path.open('r', encoding='utf-8') as f:
        loaded = yaml.safe_load(f)
        print(f"✅ Загружен конфиг из {config_path}:\n{yaml.dump(loaded, default_flow_style=False)}")

    if not isinstance(loaded, dict):
        raise ValueError('YAML config must contain a top-level dictionary with training parameters')

    merged = dict(DEFAULT_TRAIN_ARGS)
    merged.update(loaded)

    load_folder_file = merged.get('load_folder_file')
    if isinstance(load_folder_file, list):
        if len(load_folder_file) != 2:
            raise ValueError("'load_folder_file' must contain exactly 2 items: [folder, filename]")
        merged['load_folder_file'] = (load_folder_file[0], load_folder_file[1])
    elif not isinstance(load_folder_file, tuple):
        raise ValueError("'load_folder_file' must be a list or tuple with 2 items")

    return dotdict(merged)


def main():
    cli_args = parse_cli_args()
    args = load_train_args(cli_args.config)

    log.info('Loaded training config from %s', cli_args.config)

    log.info('Loading %s...', Game.__name__)
    g = Game()

    log.info('Loading %s...', nn.__name__)
    nnet = nn(g)

    if args.load_model:
        log.info('Loading checkpoint "%s/%s"...', args.load_folder_file[0], args.load_folder_file[1])
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
    else:
        log.warning('Not loading a checkpoint!')

    log.info('Loading the Coach...')
    c = Coach(g, nnet, args)

    if args.load_model:
        log.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    log.info('Starting the learning process 🎉')
    c.learn()


if __name__ == "__main__":
    main()
