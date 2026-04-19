from typing import Tuple

import numpy as np
import numpy.typing as npt

from core.game_state import GameState


class Game():
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    See othello/OthelloGame.py for an example implementation.
    """
    def __init__(self):
        pass

    def getInitBoard(self) -> GameState:
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        raise NotImplementedError()

    def getBoardSize(self) -> Tuple[int, int]:
        """
        Returns:
            (x,y): a tuple of board dimensions
        """
        raise NotImplementedError()

    def getActionSize(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        raise NotImplementedError()

    def getNextState(self, board: GameState, player: int, action: int) -> Tuple[GameState, int]:
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        raise NotImplementedError()

    def getValidMoves(self, board: GameState, player: int) -> npt.NDArray[np.int8]:
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        raise NotImplementedError()

    def getGameEnded(self, board: GameState, player: int) -> int:
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.
               
        """
        raise NotImplementedError()

    def getCanonicalForm(self, board: GameState, player: int) -> GameState:
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
        raise NotImplementedError()

    def getSymmetries(self, board: GameState, pi) -> list[tuple[GameState, npt.NDArray[np.float32]]]:
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        raise NotImplementedError()

    def toNetworkInput(self, board: GameState) -> npt.NDArray[np.float32]:
        """
        Convert game state to neural network input (matrix).

        Input:
            board: current board (GameState or equivalent)

        Returns:
            networkInput: numpy array suitable for neural network prediction
        """
        raise NotImplementedError()

    def stringRepresentation(self, board: GameState) -> str:
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        raise NotImplementedError()
