import logging
import sys
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

args = dotdict({
    'numIters': 5,
    'numEps': 5, #100,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 15,        #
    'updateThreshold': 0.6,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 200000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 25,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 2, #40,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 0.5,

    'checkpoint': './temp2/',
    'load_model': True, #False,
    'load_folder_file': ('./model_dataset/','best.pth.tar'), # /dev/models/8x100x50
    'numItersForTrainExamplesHistory': 20,

})


def main():
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
