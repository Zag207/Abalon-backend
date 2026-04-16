import torch
import numpy as np

from AbalonAiGameState import AbalonAiGameState
from network_utils import board_to_three_masks

x = torch.rand(5, 3)
y = np.zeros((2, 3))

print(x)
print(y)

test_game = AbalonAiGameState()
print(board_to_three_masks(test_game.getInitBoard()))


device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu" # type: ignore
print(f"Using {device} device")
