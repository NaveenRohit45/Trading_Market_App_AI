"""
Reinforcement Learning Layer — Part 1: Trading Environment

RL is a fundamentally different problem from the ML/LSTM layers.
Those predict WHAT the market will do. This learns WHEN TO ACT --
a policy for entry/exit/hold given the current state, trained by
trial and reward, not labeled examples.

CRITICAL SAFETY NOTE: this environment replays your own logged
candles (from the `candles` table -- same data train_lstm.py uses).
The agent trains entirely in this simulation. Do NOT wire an RL
agent's actions directly to real order placement without an extended
paper-trading validation period first -- RL agents are notorious for
finding degenerate reward-hacking strategies (e.g. overtrading to
harvest small simulated edges that don't survive real slippage/fees).

This is a SPARSE, SIMPLE environment intentionally -- start here,
don't reach for exotic reward shaping until this baseline is proven
to learn anything sensible at all (e.g. does it learn to avoid
trading in flat/choppy stretches?).
"""

from __future__ import annotations

import sqlite3
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from backend.config import settings

# Actions: 0 = HOLD (flat), 1 = LONG, 2 = SHORT
HOLD, LONG, SHORT = 0, 1, 2

LOOKBACK = 20         # candles of context the agent sees
TRANSACTION_COST_PCT = 0.03  # round-trip cost assumption (brokerage+slippage) -- tune to reality


def load_candles(symbol: str) -> np.ndarray:
    conn = sqlite3.connect(str(settings.db_path))
    rows = conn.execute(
        "SELECT open, high, low, close, volume FROM candles WHERE symbol=? ORDER BY ts ASC",
        (symbol,),
    ).fetchall()
    conn.close()
    return np.array(rows, dtype=np.float32)


class ScalpingEnv(gym.Env):
    """
    One episode = one continuous run through the historical candle
    series for a symbol. At each step the agent sees the last
    LOOKBACK candles (normalized) plus its current position, and
    chooses HOLD / LONG / SHORT. Reward is the P&L change since the
    last step, minus transaction cost when a position is opened or
    flipped.
    """

    metadata = {"render_modes": []}

    def __init__(self, symbol: str = "NIFTY"):
        super().__init__()

        self.candles = load_candles(symbol)

        if len(self.candles) < LOOKBACK + 10:
            raise ValueError(
                f"Not enough candle history for {symbol} to build an "
                f"environment ({len(self.candles)} rows). Let the app "
                f"log more live data first (see database.py candles table)."
            )

        self.closes = self.candles[:, 3]

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(LOOKBACK * 5 + 1,),  # candles flattened + position
            dtype=np.float32,
        )

        self.position = HOLD
        self.entry_price = 0.0
        self.idx = LOOKBACK

    def _get_obs(self):
        window = self.candles[self.idx - LOOKBACK: self.idx]
        mean = window.mean(axis=0, keepdims=True)
        std = window.std(axis=0, keepdims=True) + 1e-8
        norm_window = ((window - mean) / std).flatten()
        return np.concatenate([norm_window, [float(self.position)]]).astype(np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.idx = LOOKBACK
        self.position = HOLD
        self.entry_price = 0.0
        return self._get_obs(), {}

    def step(self, action):
        current_price = self.closes[self.idx]
        reward = 0.0

        # Mark-to-market P&L on existing position before acting.
        if self.position == LONG:
            reward += (current_price - self.entry_price) / self.entry_price * 100
        elif self.position == SHORT:
            reward += (self.entry_price - current_price) / self.entry_price * 100

        # Apply the new action.
        if action != self.position:
            if action in (LONG, SHORT):
                reward -= TRANSACTION_COST_PCT  # cost of opening/flipping
                self.entry_price = current_price
            self.position = action

        self.idx += 1
        terminated = self.idx >= len(self.closes) - 1
        truncated = False

        return self._get_obs(), reward, terminated, truncated, {}
