import torch
import numpy as np

from aiBot.AbalonAiGameState import AbalonAiGameState
from aiBot.game_state_utils import get_matrix_from_board
from aiBot.network_utils import board_to_three_masks

x = torch.rand(5, 3)
y = np.zeros((2, 3))

print(x)
print(y)

test_game = AbalonAiGameState()
init_board = test_game.getInitBoard()
board_matrix = get_matrix_from_board(init_board)
print(board_matrix)
print(board_to_three_masks(board_matrix))

print(test_game.stringRepresentation(init_board))

device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu" # type: ignore
print(f"Using {device} device")

valid_mask = test_game.getValidMoves(init_board, 1)
print(valid_mask)
