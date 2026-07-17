"""
Deep Learning Layer — LSTM Sequence Model

Unlike train_model.py (RandomForest on a single snapshot of
indicators), this learns from the SEQUENCE of the last N candles --
closer to how a human actually reads a chart, and capable of learning
temporal patterns the tabular model can't see.

REQUIRES THE SAME THING THE ML LAYER DOES: real accumulated live data.
LSTMs are MORE data-hungry than RandomForest, not less -- do not run
this until train_model.py is already showing meaningful row counts
(see MIN_ROWS_TO_TRAIN there). If anything, wait longer for this one.

Run manually once you have enough data:
    python -m backend.prediction.train_lstm

Usage of the trained model happens in prediction/ml_predictor.py --
the loader there checks for an LSTM checkpoint first and falls back to
the RandomForest if none exists.
"""

from __future__ import annotations

import sqlite3
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from backend.config import settings

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

SEQUENCE_LENGTH = 20   # last 20 candles feed each prediction
MIN_ROWS_TO_TRAIN = 500  # LSTMs need MORE data than RandomForest, not less
DIRECTION_MAP = {"UP": 0, "DOWN": 1, "SIDEWAYS": 2}
REVERSE_MAP = {v: k for k, v in DIRECTION_MAP.items()}


class CandleLSTM(nn.Module):
    """
    Small, deliberately shallow LSTM. With limited real trading data
    (thousands of rows, not millions), a large/deep network will just
    memorize noise. Keep it small until you have proof it needs to be
    bigger.
    """

    def __init__(self, n_features: int, hidden_size: int = 32, n_classes: int = 3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True,
        )
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(hidden_size, n_classes)

    def forward(self, x):
        _, (hidden, _) = self.lstm(x)
        out = self.dropout(hidden[-1])
        return self.fc(out)


class CandleSequenceDataset(Dataset):
    def __init__(self, sequences: np.ndarray, labels: np.ndarray):
        self.X = torch.tensor(sequences, dtype=torch.float32)
        self.y = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def load_candle_history(symbol: str) -> pd.DataFrame:
    """
    Pulls raw candles logged over time. NOTE: this assumes you are
    also persisting raw candles somewhere queryable -- if you're only
    storing predictions (see database.py), you'll need to add a
    candles table that the live loop appends to each minute. This
    function documents the expected shape; wire it to your actual
    candle storage once that table exists.
    """

    conn = sqlite3.connect(str(settings.db_path))
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT ts, open, high, low, close, volume
        FROM candles
        WHERE symbol = ?
        ORDER BY ts ASC
        """,
        (symbol,),
    ).fetchall()

    conn.close()

    return pd.DataFrame([dict(r) for r in rows])


def build_sequences(df: pd.DataFrame, seq_len: int = SEQUENCE_LENGTH):
    """
    Turns a flat candle dataframe into overlapping sequences of
    [seq_len] candles each, with the label being the direction of the
    NEXT candle after the sequence ends (simple next-step direction --
    swap in your actual resolved-prediction outcomes if you want to
    match exactly what the app scores as "correct").
    """

    feature_cols = ["open", "high", "low", "close", "volume"]

    values = df[feature_cols].values
    closes = df["close"].values

    X, y = [], []

    for i in range(len(values) - seq_len - 1):
        window = values[i: i + seq_len]

        next_close = closes[i + seq_len]
        last_close = closes[i + seq_len - 1]

        change_pct = (next_close - last_close) / last_close * 100

        if change_pct > 0.05:
            label = DIRECTION_MAP["UP"]
        elif change_pct < -0.05:
            label = DIRECTION_MAP["DOWN"]
        else:
            label = DIRECTION_MAP["SIDEWAYS"]

        X.append(window)
        y.append(label)

    return np.array(X), np.array(y)


def train_for_symbol(symbol: str):
    df = load_candle_history(symbol)

    if len(df) < MIN_ROWS_TO_TRAIN:
        print(
            f"⏭️  Skipping {symbol} — only {len(df)} candles logged "
            f"(need {MIN_ROWS_TO_TRAIN}+). Let the app run longer, and "
            f"make sure candles are actually being persisted to a "
            f"'candles' table (see load_candle_history docstring)."
        )
        return

    X, y = build_sequences(df)

    if len(X) < 50:
        print(f"⏭️  Skipping {symbol} — not enough sequences after windowing.")
        return

    # Normalize features (critical for LSTM training stability).
    mean = X.mean(axis=(0, 1), keepdims=True)
    std = X.std(axis=(0, 1), keepdims=True) + 1e-8
    X = (X - mean) / std

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    train_ds = CandleSequenceDataset(X_train, y_train)
    test_ds = CandleSequenceDataset(X_test, y_test)

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=32)

    model = CandleLSTM(n_features=X.shape[-1])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    EPOCHS = 30
    best_val_acc = 0.0

    for epoch in range(EPOCHS):
        model.train()
        for xb, yb in train_loader:
            optimizer.zero_grad()
            out = model(xb)
            loss = criterion(out, yb)
            loss.backward()
            optimizer.step()

        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for xb, yb in test_loader:
                preds = model(xb).argmax(dim=1)
                correct += (preds == yb).sum().item()
                total += len(yb)

        val_acc = correct / total if total else 0.0
        best_val_acc = max(best_val_acc, val_acc)

        if epoch % 5 == 0 or epoch == EPOCHS - 1:
            print(f"{symbol} epoch {epoch:>2} — val accuracy: {val_acc:.1%}")

    print(f"\n{symbol}: best validation accuracy = {best_val_acc:.1%}")
    print(
        "Compare this against your V1 heuristic AND the RandomForest "
        "from train_model.py on the same symbol -- only keep whichever "
        "actually wins on real held-out data.\n"
    )

    torch.save(
        {
            "model_state": model.state_dict(),
            "n_features": X.shape[-1],
            "mean": mean,
            "std": std,
            "seq_len": SEQUENCE_LENGTH,
        },
        MODELS_DIR / f"{symbol}_lstm.pt",
    )


def main():
    for symbol in ("NIFTY", "SENSEX"):
        train_for_symbol(symbol)


if __name__ == "__main__":
    main()
