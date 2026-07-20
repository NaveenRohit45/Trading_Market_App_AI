"""
Multi-Model Training — Phase 4

Trains XGBoost, LightGBM, and CatBoost alongside the existing
RandomForest (train_model.py), on the EXACT same data and
time-respecting split, and prints a direct comparison so you can see
which one actually wins on YOUR real data -- not which one sounds
most impressive.

HONEST NOTE on the rest of Phase 4's wishlist:
- Transformer / Temporal Fusion Transformer: need far more data than
  you currently have (thousands to tens of thousands of resolved
  rows) to avoid pure overfitting. Revisit once train_model.py and
  this script show train_lstm.py-scale data volumes.
- TabPFN: interesting because it's specifically designed for SMALL
  tabular datasets (a few hundred to few thousand rows) unlike most
  deep models -- worth trying once you're past ~1000 resolved rows
  per symbol/horizon. Not wired in yet; flagging as a real next step,
  not dismissing it.
- TimeGPT: requires a paid Nixtla API subscription -- a genuine
  external cost decision, not a code decision. Not wired in until you
  decide that's worth paying for.

Run manually once you have enough data (same MIN_ROWS_TO_TRAIN
threshold as train_model.py):

    python -m backend.prediction.train_multi_model
"""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score

from backend.prediction.train_model import (
    load_resolved_predictions,
    prepare_features,
    MIN_ROWS_TO_TRAIN,
)

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def _get_model_candidates():
    """Returns {name: model_instance} for every library that's
    actually installed -- skips gracefully if one isn't, rather than
    crashing the whole comparison."""

    candidates = {}

    try:
        from xgboost import XGBClassifier
        candidates["XGBoost"] = XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            eval_metric="mlogloss", random_state=42,
        )
    except ImportError:
        print("⏭️  xgboost not installed, skipping")

    try:
        from lightgbm import LGBMClassifier
        candidates["LightGBM"] = LGBMClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            random_state=42, verbose=-1,
        )
    except ImportError:
        print("⏭️  lightgbm not installed, skipping")

    try:
        from catboost import CatBoostClassifier
        candidates["CatBoost"] = CatBoostClassifier(
            iterations=200, depth=4, learning_rate=0.05,
            random_state=42, verbose=False,
        )
    except ImportError:
        print("⏭️  catboost not installed, skipping")

    return candidates


def train_and_compare_for(df, symbol: str, horizon: int):
    subset = df[(df.symbol == symbol) & (df.horizon == horizon)].copy()

    if len(subset) < MIN_ROWS_TO_TRAIN:
        print(
            f"⏭️  Skipping {symbol} {horizon}m -- only {len(subset)} rows "
            f"(need {MIN_ROWS_TO_TRAIN}+)."
        )
        return

    subset = prepare_features(subset)

    split_idx = int(len(subset) * 0.8)
    train_df = subset.iloc[:split_idx]
    test_df = subset.iloc[split_idx:]

    feature_cols = [
        c for c in subset.columns
        if c not in ("ts", "symbol", "horizon", "actual_direction", "correct")
    ]

    X_train = train_df[feature_cols].fillna(0)
    y_train = train_df["actual_direction"]
    X_test = test_df[feature_cols].fillna(0)
    y_test = test_df["actual_direction"]

    candidates = _get_model_candidates()

    if not candidates:
        print("No boosting libraries installed -- run: pip install xgboost lightgbm catboost")
        return

    results = {}

    print(f"\n{'=' * 60}")
    print(f"{symbol} — {horizon}m — {len(subset)} rows")
    print(f"{'=' * 60}")

    # Also show the existing V1 heuristic's real accuracy on this
    # exact test slice, so new models are judged against the thing
    # actually running in production, not just each other.
    heuristic_accuracy = test_df["correct"].mean()
    print(f"Existing V1 heuristic (reference): {heuristic_accuracy:.1%}")

    for name, model in candidates.items():
        try:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            results[name] = (acc, model)
            print(f"{name:12s}: {acc:.1%}")
        except Exception as error:
            print(f"{name:12s}: FAILED -- {error}")

    if not results:
        return

    best_name, (best_acc, best_model) = max(results.items(), key=lambda kv: kv[1][0])

    print(f"\nBest: {best_name} ({best_acc:.1%})")

    if best_acc <= heuristic_accuracy:
        print(
            "None of these beat the existing V1 heuristic on this "
            "data -- NOT saving a replacement model. This is a valid, "
            "useful result: it means your simpler heuristic is "
            "currently doing fine, not that something went wrong."
        )
        return

    model_path = MODELS_DIR / f"{symbol}_{horizon}m_{best_name.lower()}.joblib"
    joblib.dump({"model": best_model, "feature_cols": feature_cols, "type": best_name}, model_path)
    print(f"💾 Saved: {model_path}")


def main():
    df = load_resolved_predictions()

    print(f"Loaded {len(df)} resolved predictions with feature data.")

    if df.empty:
        print("No data yet -- same requirement as train_model.py.")
        return

    for symbol in df["symbol"].unique():
        for horizon in sorted(df[df.symbol == symbol]["horizon"].unique()):
            train_and_compare_for(df, symbol, int(horizon))


if __name__ == "__main__":
    main()
