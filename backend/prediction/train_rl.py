"""
Reinforcement Learning Layer — Part 2: DQN Agent

Trains a Deep Q-Network against ScalpingEnv (rl_environment.py) using
replayed historical candles. Run manually once you have enough logged
candle history:

    python -m backend.prediction.train_rl

OUTPUT: models/<symbol>_dqn.pt

WHAT TO DO WITH THE RESULT: do not connect this to real order
placement. Use it as a research signal alongside the other layers --
compare its simulated backtest return against a simple buy-and-hold
or your existing V1 heuristic on the SAME historical stretch before
trusting it for anything. RL agents can look great in backtest and
fail completely on live data (regime change, overfitting to specific
historical noise) -- this risk is higher for RL than for the
supervised ML/LSTM layers.
"""

from __future__ import annotations

import random
from collections import deque
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from backend.prediction.rl_environment import ScalpingEnv

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


class QNetwork(nn.Module):
    def __init__(self, obs_dim: int, n_actions: int = 3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, n_actions),
        )

    def forward(self, x):
        return self.net(x)


class ReplayBuffer:
    def __init__(self, capacity=20000):
        self.buffer = deque(maxlen=capacity)

    def push(self, s, a, r, s2, done):
        self.buffer.append((s, a, r, s2, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        s, a, r, s2, done = zip(*batch)
        return (
            torch.tensor(np.array(s), dtype=torch.float32),
            torch.tensor(a, dtype=torch.long),
            torch.tensor(r, dtype=torch.float32),
            torch.tensor(np.array(s2), dtype=torch.float32),
            torch.tensor(done, dtype=torch.float32),
        )

    def __len__(self):
        return len(self.buffer)


def train_dqn(symbol: str, episodes: int = 30):
    try:
        env = ScalpingEnv(symbol)
    except ValueError as error:
        print(f"⏭️  Skipping {symbol}: {error}")
        return

    obs_dim = env.observation_space.shape[0]

    q_net = QNetwork(obs_dim)
    target_net = QNetwork(obs_dim)
    target_net.load_state_dict(q_net.state_dict())

    optimizer = torch.optim.Adam(q_net.parameters(), lr=1e-3)
    buffer = ReplayBuffer()

    gamma = 0.95
    batch_size = 64
    epsilon = 1.0
    epsilon_min = 0.05
    epsilon_decay = 0.97
    target_update_every = 5

    episode_returns = []

    for episode in range(episodes):
        obs, _ = env.reset()
        total_reward = 0.0
        done = False

        while not done:
            if random.random() < epsilon:
                action = env.action_space.sample()
            else:
                with torch.no_grad():
                    q_values = q_net(torch.tensor(obs, dtype=torch.float32).unsqueeze(0))
                    action = int(q_values.argmax().item())

            next_obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            buffer.push(obs, action, reward, next_obs, float(done))
            obs = next_obs
            total_reward += reward

            if len(buffer) >= batch_size:
                s, a, r, s2, d = buffer.sample(batch_size)

                with torch.no_grad():
                    max_next_q = target_net(s2).max(dim=1).values
                    target_q = r + gamma * max_next_q * (1 - d)

                current_q = q_net(s).gather(1, a.unsqueeze(1)).squeeze(1)

                loss = nn.functional.mse_loss(current_q, target_q)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        epsilon = max(epsilon_min, epsilon * epsilon_decay)
        episode_returns.append(total_reward)

        if episode % target_update_every == 0:
            target_net.load_state_dict(q_net.state_dict())

        print(f"{symbol} episode {episode:>2} — simulated return: {total_reward:+.2f}% — epsilon {epsilon:.2f}")

    avg_last_5 = np.mean(episode_returns[-5:])
    print(f"\n{symbol}: average simulated return over last 5 episodes = {avg_last_5:+.2f}%")
    print(
        "Compare this to buy-and-hold return over the same historical "
        "stretch, and to your V1 heuristic's real accuracy. A positive "
        "number here does NOT mean it will work live -- it means it "
        "found SOME pattern in this specific historical replay.\n"
    )

    torch.save(
        {"model_state": q_net.state_dict(), "obs_dim": obs_dim},
        MODELS_DIR / f"{symbol}_dqn.pt",
    )


def main():
    for symbol in ("NIFTY", "SENSEX"):
        train_dqn(symbol)


if __name__ == "__main__":
    main()
