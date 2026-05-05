from dataclasses import dataclass
from tkinter import W
from typing import List

import numpy as np

from aiBot.NumpyAbalonAiGame import NumpyAbalonAiGame
from aiBot.base_alpha_zero.MCTS import MCTS
from aiBot.base_alpha_zero.NeuralNet import NeuralNet
from aiBot.game_state_utils import get_team_code
from aiBot.neural_net import AbalonNNet
from aiBot.utils import dotdict
from core.board.circle import Circle
from core.board.circle_team import CircleTeam
from core.game_state import GameState
from core.movement.moving_directions import MovingDirections
from utils.GameStateConverter import GameStateConverter

@dataclass
class Moving:
    circles_checked: List[Circle]
    moving_direction: MovingDirections


class Bot:
    game: GameState
    player: CircleTeam
    bot_game: NumpyAbalonAiGame
    nnet: NeuralNet
    args: dotdict

    def __init__(self, game: GameState, player: CircleTeam, args: dotdict) -> None:
        """
        Для args нужно передать cpuct, numMCTSSims
        """
        self.game = game
        self.player = player
        self.bot_game = NumpyAbalonAiGame()
        self.nnet = AbalonNNet(self.bot_game)
        self.args = args
    
    def calc_move(self) -> Moving:
        mcts = MCTS(self.bot_game, self.nnet, self.args)
        init_state = GameStateConverter.to_numpy_game_state(self.game)
        init_state_cannonical = self.bot_game.getCanonicalForm(init_state, get_team_code(self.player))
        moving_probs = mcts.getActionProb(init_state_cannonical, 0)
        moving_index = int(np.argmax(moving_probs))
        moving = self.bot_game.action_space[moving_index]

        if moving is None:
            raise ValueError("Некорректный ход")

        return Moving([Circle(circle_coords, self.player) for circle_coords in moving.selected_coords], moving.direction) 
