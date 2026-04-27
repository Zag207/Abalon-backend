import os
from typing import Tuple

import numpy as np
import numpy.typing as npt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from aiBot.base_alpha_zero.NeuralNet import NeuralNet


class AbalonResNet(nn.Module):
    """
    ResNet-based neural network for Abalon game.
    Input: 3-channel 9x9 board representation (white, black, forbidden).
    Output: (policy vector, value scalar).
    """

    def __init__(self, action_size: int, num_resblocks: int = 6, channels: int = 64):
        super().__init__()
        self.action_size = action_size
        self.channels = channels

        # Input convolution
        self.input_conv = nn.Sequential(
            nn.Conv2d(3, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
        )

        # Residual blocks
        self.resblocks = nn.ModuleList([self._make_resblock(channels) for _ in range(num_resblocks)])

        # Policy head
        self.policy_conv = nn.Conv2d(channels, 32, kernel_size=3, padding=1)
        self.policy_bn = nn.BatchNorm2d(32)
        self.policy_fc = nn.Linear(32 * 9 * 9, action_size)

        # Value head
        self.value_conv = nn.Conv2d(channels, 16, kernel_size=3, padding=1)
        self.value_bn = nn.BatchNorm2d(16)
        self.value_fc1 = nn.Linear(16 * 9 * 9, 128)
        self.value_fc2 = nn.Linear(128, 1)

    @staticmethod
    def _make_resblock(channels: int) -> nn.Module:
        return nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x = self.input_conv(x)

        for resblock in self.resblocks:
            x = x + resblock(x)  # Skip connection

        # Policy head
        p = self.policy_conv(x)
        p = self.policy_bn(p)
        p = torch.relu(p)
        p = p.view(p.size(0), -1)
        p = self.policy_fc(p)
        p = torch.softmax(p, dim=1)

        # Value head
        v = self.value_conv(x)
        v = self.value_bn(v)
        v = torch.relu(v)
        v = v.view(v.size(0), -1)
        v = self.value_fc1(v)
        v = torch.relu(v)
        v = self.value_fc2(v)
        v = torch.tanh(v)

        return p, v


class AbalonNNet(NeuralNet):
    """
    Neural network implementation for Abalon game using PyTorch.
    Wraps AbalonResNet for training and prediction.
    """

    def __init__(self, game, lr: float = 0.0001, weight_decay: float = 0.0001, num_resblocks: int = 6, channels: int = 64):
        self.game = game
        self.action_size = game.getActionSize()
        self.lr = lr
        self.weight_decay = weight_decay

        # Determine device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Create model
        self.model = AbalonResNet(self.action_size, num_resblocks=num_resblocks, channels=channels).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=self.weight_decay)

    def train(self, examples: list) -> float:
        """
        Train the neural network on examples.

        Input:
            examples: list of (board, pi, v) tuples where:
                - board: network input (numpy array 3x9x9)
                - pi: policy vector (numpy array)
                - v: game value (-1, 0, 1)
        
        Returns:
            float: average loss over all epochs
        """
        if len(examples) == 0:
            return 0.0

        boards = np.array([ex[0] for ex in examples], dtype=np.float32)
        pis = np.array([ex[1] for ex in examples], dtype=np.float32)
        vs = np.array([ex[2] for ex in examples], dtype=np.float32)

        # Create dataset and dataloader
        dataset = TensorDataset(
            torch.from_numpy(boards).to(self.device),
            torch.from_numpy(pis).to(self.device),
            torch.from_numpy(vs).to(self.device),
        )
        batch_size = min(32, len(examples) // 2 + 1)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model.train()
        all_epoch_losses = []
        
        for epoch in range(10):
            total_loss = 0.0
            num_batches = 0
            
            for batch_boards, batch_pis, batch_vs in dataloader:
                self.optimizer.zero_grad()

                # Forward pass
                p_pred, v_pred = self.model(batch_boards)

                # Loss: policy loss (cross-entropy) + value loss (MSE)
                policy_loss = -torch.sum(batch_pis * torch.log(p_pred + 1e-8)) / batch_boards.size(0)
                value_loss = torch.mean((v_pred.squeeze() - batch_vs) ** 2)
                loss = policy_loss + value_loss

                # Backward pass
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()
                num_batches += 1
            
            avg_epoch_loss = total_loss / num_batches if num_batches > 0 else 0.0
            all_epoch_losses.append(avg_epoch_loss)
        
        avg_loss = sum(all_epoch_losses) / len(all_epoch_losses) if all_epoch_losses else 0.0
        return avg_loss

    def predict(self, board: npt.NDArray[np.float32]) -> Tuple[npt.NDArray[np.float32], float]:
        """
        Predict policy and value for a given board.

        Input:
            board: network input (numpy array 3x9x9 float32)

        Returns:
            pi: policy vector (numpy array)
            v: value estimate (float)
        """
        self.model.eval()
        with torch.no_grad():
            board_tensor = torch.from_numpy(board).unsqueeze(0).to(self.device)
            p, v = self.model(board_tensor)

            pi = p.cpu().numpy()[0]
            value = v.cpu().item()

        return pi, value

    def save_checkpoint(self, folder: str, filename: str) -> None:
        """Save model checkpoint."""
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, filename)
        torch.save(self.model.state_dict(), filepath)

    def load_checkpoint(self, folder: str, filename: str) -> None:
        """Load model checkpoint."""
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            self.model.load_state_dict(torch.load(filepath, map_location=self.device))
