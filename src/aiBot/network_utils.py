import numpy as np
import numpy.typing as npt


def board_to_three_masks(board: npt.NDArray[np.integer]) -> npt.NDArray[np.float32]:
	"""
	Converts encoded board matrix to a 3-channel mask tensor (C, H, W).

	Board encoding:
	- 1: white pieces
	- -1: black pieces
	- 2: forbidden/outside-hex cells
	"""
	white_mask = (board == 1).astype(np.float32)
	black_mask = (board == -1).astype(np.float32)
	forbidden_mask = (board == 2).astype(np.float32)

	return np.stack([white_mask, black_mask, forbidden_mask], axis=0)
