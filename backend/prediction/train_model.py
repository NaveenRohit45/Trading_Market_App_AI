"""
Train Model — Phase 3

Trains a real ML classifier on the predictions your live app has
accumulated (see store_predictions() in market_service.py, which now
saves a feature snapshot with every prediction).

Run this manually / on a schedule (e.g. weekly cron) once you have
enough resolved rows:

    python -m backend.prediction.train_model

It reads resolved predictions from data/market_intelligence.db, builds
a feature matrix, trains one RandomForestClassifier per
(symbol, horizon), evaluates it with a time-respecting split, and
saves each model to models/<symbol>_<horizon>m.joblib

DO NOT trust this until you have a few hundred resolved rows per
(symbol, horizon) combo at minimum -- with fewer rows the model will
just memorize noise. Check the printed accuracy / row counts before
believing the output.
"""

from __future__ import annotations

import sqlite3
import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

from backend.config import settings

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

FEATURE_COLUMNS = [
    "rsi",
    "ema_fast",
    "ema_slow",
    "atr",
    "momentum",
    "support",
    "resistance",
    "news_score",
]

CATEGORICAL_COLUMNS = [
    "state",
    "regime",
    "breakout",
    "peer_state",
]

MIN_ROWS_TO_TRAIN = 200  # don't bother below this -- results are noise


def load_resolved_predictions() -> pd.DataFrame:
    conn = sqlite3.connect(str(settings.db_path))
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT ts, symbol, horizon, price, direction, confidence,
               features, actual_direction, correct
        FROM predictions
        WHERE resolved = 1 AND features IS NOT NULL
        ORDER BY ts ASC
        """
    ).fetchall()

    conn.close()

    records = []

    for row in rows:
        try:
            feats = json.loads(row["features"])
        except (TypeError, json.JSONDecodeError):
            continue

        record = {
            "ts": row["ts"],
            "symbol": row["symbol"],
            "horizon": row["horizon"],
            "predicted_direction": row["direction"],
            "actual_direction": row["actual_direction"],
            "correct": row["correct"],
            **feats,
        }

        records.append(record)

    return pd.DataFrame.from_records(records)


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # One-hot encode categorical market-state columns.
    df = pd.get_dummies(
        df,
        columns=[c for c in CATEGORICAL_COLUMNS if c in df.columns],
        dummy_na=True,
    )

    # Also encode what the heuristic V1 engine predicted -- the model
    # can learn "V1 tends to be wrong when it says X in state Y".
    df = pd.get_dummies(df, columns=["predicted_direction"], prefix="v1_pred")

    return df


def train_for(df: pd.DataFrame, symbol: str, horizon: int):
    subset = df[(df.symbol == symbol) & (df.horizon == horizon)].copy()

    if len(subset) < MIN_ROWS_TO_TRAIN:
        print(
            f"⏭️  Skipping {symbol} {horizon}m — only {len(subset)} rows "
            f"(need {MIN_ROWS_TO_TRAIN}+). Let the app run longer."
        )
        return

    subset = prepare_features(subset)

    # Time-respecting split: train on the older 80%, test on the
    # newest 20%. Never shuffle time-series data randomly -- that
    # leaks future information into training and gives a fake-good
    # accuracy score.
    split_idx = int(len(subset) * 0.8)
    train_df = subset.iloc[:split_idx]
    test_df = subset.iloc[split_idx:]

    feature_cols = [
        c for c in subset.columns
        if c not in (
            "ts", "symbol", "horizon", "actual_direction",
            "correct",
        )
    ]

    X_train = train_df[feature_cols].fillna(0)
    y_train = train_df["actual_direction"]

    X_test = test_df[feature_cols].fillna(0)
    y_test = test_df["actual_direction"]

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,           # keep shallow -- small dataset, avoid overfit
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    print(f"\n{'=' * 60}")
    print(f"{symbol} — {horizon} minute horizon — {len(subset)} rows")
    print(f"{'=' * 60}")
    print(classification_report(y_test, preds, zero_division=0))

    # Compare against the existing heuristic's own accuracy on the
    # same test rows, so you can see if the ML model is actually
    # better before switching to it.
    heuristic_correct = test_df["correct"].mean()
    print(f"Existing V1 heuristic accuracy on this test slice: {heuristic_correct:.1%}")

    model_path = MODELS_DIR / f"{symbol}_{horizon}m.joblib"
    joblib.dump(
        {"model": model, "feature_cols": feature_cols},
        model_path,
    )
    print(f"💾 Saved: {model_path}")


def main():
    df = load_resolved_predictions()

    print(f"Loaded {len(df)} resolved predictions with feature data.")

    if df.empty:
        print(
            "No resolved predictions with features found yet.\n"
            "Make sure the app has been running live (APP_MODE=GROWW) "
            "for a while -- predictions only resolve after their "
            "horizon elapses, and features are only saved from now on."
        )
        return

    for symbol in df["symbol"].unique():
        for horizon in sorted(df[df.symbol == symbol]["horizon"].unique()):
            train_for(df, symbol, int(horizon))


if __name__ == "__main__":
    main()
