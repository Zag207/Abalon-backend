import logging
import os
import sys
from collections import deque
from pickle import Pickler, Unpickler
from random import shuffle

from tqdm import tqdm

from .Arena import Arena
from .MCTS import MCTS

# Абсолютный импорт для metrics (aiBot в sys.path добавляется в train_bot.py)
try:
    from metrics import MetricsCollector, GameMetrics
except ImportError:
    # Fallback для относительного импорта если aiBot не в sys.path
    from ..metrics import MetricsCollector, GameMetrics

import numpy as np

log = logging.getLogger(__name__)

class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)
        self.trainExamplesHistory = []  # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False  # can be overriden in loadTrainExamples()
        self.metrics_collector = MetricsCollector()

    def executeEpisode(self, episode_num: int = 0):
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            trainExamples: a list of examples of the form (canonicalBoard, currPlayer, pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        trainExamples = []
        board = self.game.getInitBoard()
        self.curPlayer = 1
        episodeStep = 0

        log.info("Эпизод self-play начался")

        while True:
            episodeStep += 1
            current_player_name = "Белые" if self.curPlayer == 1 else "Черные"
            
            # Проверка лимита ходов
            if board.move_count > 200:
                log.error(f"⚠️ КРИТИЧЕСКАЯ ОШИБКА! Счетчик ходов превышен: {board.move_count}/200")
            
            # log.warning(f"[Ход {episodeStep}] Ход: {current_player_name} | Счет: Белые={board.score_white} Черные={board.score_black} | Ходов всего: {board.move_count}/200")
            
            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer)
            temp = int(episodeStep < self.args.tempThreshold)

            pi = self.mcts.getActionProb(canonicalBoard, temp=temp)
            sym = self.game.getSymmetries(canonicalBoard, pi)
            for b, p in sym:
                trainExamples.append([b, self.curPlayer, p, None])

            action = np.random.choice(len(pi), p=pi)
            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action)

            r = self.game.getGameEnded(board, self.curPlayer)

            # log.info(f"Шаг эпизода: {episodeStep}")

            if r is not None:
                end_type = board.get_game_end_type()
                if end_type == 'score_win':
                    winner_name = "Белые" if board.score_white >= 6 else "Черные"
                    log.info(f"🏁 Эпизод закончен ТРАДИЦИОННОЙ ПОБЕДОЙ! Победитель: {winner_name}")
                    winner = "White" if board.score_white >= 6 else "Black"
                elif end_type == 'moves_limit':
                    if board.score_white > board.score_black:
                        winner_name = "Белые"
                        winner = "White"
                    elif board.score_white < board.score_black:
                        winner_name = "Черные"
                        winner = "Black"
                    else:
                        winner_name = "НИЧЬЯ"
                        winner = "Draw"
                    log.info(f"🏁 Эпизод закончен по ЛИМИТУ ХОДОВ (200 ходов)! Результат: {winner_name} | Счет: Белые={board.score_white} Черные={board.score_black}")
                else:
                    log.info(f"🏁 Эпизод закончен неизвестным образом")
                    winner = "Unknown"
                
                # Создаем объект метрик игры
                metrics = GameMetrics(
                    episode_num=episode_num,
                    move_count=board.move_count,
                    white_score=board.score_white,
                    black_score=board.score_black,
                    end_type=end_type,
                    winner=winner,
                    value=r if r is not None else 0.0,
                )
                
                return (
                    [(self.game.toNetworkInput(x[0]), x[2], r * ((-1) ** (x[1] != self.curPlayer))) for x in trainExamples],
                    metrics
                )

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximum length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """

        for i in range(1, self.args.numIters + 1):
            # bookkeeping
            log.info(f'Starting Iter #{i} ...')
            
            # Начало новой итерации метрик
            self.metrics_collector.start_iteration(i, self.args.numEps)
            
            # examples of the iteration
            if not self.skipFirstSelfPlay or i > 1:
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)
                
                episode_num = 0
                for _ in tqdm(range(self.args.numEps), desc="Self Play"):
                    episode_num += 1
                    self.mcts = MCTS(self.game, self.nnet, self.args)  # reset search tree
                    examples, metrics = self.executeEpisode(episode_num)
                    iterationTrainExamples.extend(examples)
                    
                    # Добавляем метрики игры
                    self.metrics_collector.add_game(
                        episode_num=metrics.episode_num,
                        move_count=metrics.move_count,
                        white_score=metrics.white_score,
                        black_score=metrics.black_score,
                        end_type=metrics.end_type,
                        winner=metrics.winner,
                        value=metrics.value,
                    )

                # save the iteration examples to the history 
                self.trainExamplesHistory.append(iterationTrainExamples)

            if len(self.trainExamplesHistory) > self.args.numItersForTrainExamplesHistory:
                log.warning(
                    f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(self.trainExamplesHistory)}")
                self.trainExamplesHistory.pop(0)
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)  
            self.saveTrainExamples(i - 1)

            # shuffle examples before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            self.pnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            pmcts = MCTS(self.game, self.pnet, self.args)

            log.info("Начало тренировки нейросети")
            train_loss = self.nnet.train(trainExamples)
            nmcts = MCTS(self.game, self.nnet, self.args)

            log.info('PITTING AGAINST PREVIOUS VERSION')
            arena = Arena(lambda x: np.argmax(pmcts.getActionProb(x, temp=0)),
                          lambda x: np.argmax(nmcts.getActionProb(x, temp=0)), self.game)
            pwins, nwins, draws = arena.playGames(self.args.arenaCompare)

            log.info('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            model_accepted = False
            if pwins + nwins == 0 or float(nwins) / (pwins + nwins) < self.args.updateThreshold:
                log.info('REJECTING NEW MODEL')
                self.nnet.load_checkpoint(folder=self.args.checkpoint, filename='temp.pth.tar')
            else:
                log.info('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar')
                model_accepted = True
            
            # Завершение итерации метрик
            self.metrics_collector.finalize_iteration(
                train_loss=train_loss,
                arena_new=(nwins, pwins, draws),
                model_accepted=model_accepted
            )

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + ".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args.load_folder_file[0], self.args.load_folder_file[1])
        examplesFile = modelFile + ".examples"
        if not os.path.isfile(examplesFile):
            log.warning(f'File "{examplesFile}" with trainExamples not found!')
            r = input("Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            log.info("File with trainExamples found. Loading it...")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            log.info('Loading done!')

            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True
