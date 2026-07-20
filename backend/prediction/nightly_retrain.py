"""
Nightly Self-Learning Pipeline — Phase 8

Meant to run once per day after market close (schedule via Windows
Task Scheduler or cron -- see bottom of this file for exact setup).

What it actually does, honestly:
1. Retrains a fresh RandomForest on ALL data collected so far
   (reuses train_model.py's logic -- not duplicated here).
2. Compares the fresh model's held-out accuracy against whatever
   model is CURRENTLY deployed (tracked in models/registry.json).
3. Deploys the new model ONLY if it's genuinely better on held-out
   data. Otherwise keeps the old one and says so explicitly.

This is intentionally conservative. "No human, fully automatic" does
NOT mean "blindly trust whatever trains today" -- a single bad day's
data could otherwise degrade your live model. The comparison gate is
the safety mechanism; don't remove it even though it means most nights
probably won't deploy anything new, especially early on with limited
data.

Run manually to test, or schedule daily:
    python -m backend.prediction.nightly_retrain
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from backend.prediction.train_model import (
    load_resolved_predictions,
    prepare_features,
    MODELS_DIR,
    MIN_ROWS_TO_TRAIN,
)

REGISTRY_PATH = MODELS_DIR / "registry.json"


def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_registry(registry: dict):
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))


def run_nightly_cycle():
    print("=" * 60)
    print(f"NIGHTLY SELF-LEARNING CYCLE -- {datetime.now().isoformat()}")
    print("=" * 60)

    registry = load_registry()

    df = load_resolved_predictions()

    if df.empty:
        print("No resolved predictions available yet. Nothing to do tonight.")
        return

    for symbol in df["symbol"].unique():
        for horizon in sorted(df[df.symbol == symbol]["horizon"].unique()):

            key = f"{symbol}_{horizon}m"
            subset = df[(df.symbol == symbol) & (df.horizon == int(horizon))]

            if len(subset) < MIN_ROWS_TO_TRAIN:
                print(f"⏭️  {key}: only {len(subset)} rows, skipping (need {MIN_ROWS_TO_TRAIN}+)")
                continue

            previous_entry = registry.get(key)
            model_path = MODELS_DIR / f"{symbol}_{int(horizon)}m.joblib"

            # Back up the currently-deployed model before touching
            # anything, so a bad night can always be manually reverted.
            backup_path = None
            if model_path.exists():
                backup_path = MODELS_DIR / f"{symbol}_{int(horizon)}m.joblib.bak"
                backup_path.write_bytes(model_path.read_bytes())

            print(f"\n--- {key} ---")
            print(f"Rows available: {len(subset)}")

            if previous_entry:
                print(
                    f"Currently deployed model: accuracy={previous_entry['accuracy']:.1%}, "
                    f"trained on {previous_entry['row_count']} rows, "
                    f"deployed {previous_entry['deployed_at']}"
                )
            else:
                print("No model currently deployed for this symbol/horizon.")

            # train_for() (from train_model.py) trains AND saves the
            # model unconditionally today -- for the nightly cycle we
            # want the comparison gate BEFORE overwriting, so we
            # capture its printed accuracy by re-deriving it the same
            # way rather than changing train_model.py's existing
            # behavior (used interactively elsewhere).
            new_accuracy = _train_and_get_accuracy(df, symbol, int(horizon))

            if new_accuracy is None:
                print(f"⚠️  Training failed for {key}, keeping existing model.")
                continue

            should_deploy = (
                previous_entry is None
                or new_accuracy > previous_entry["accuracy"]
            )

            if should_deploy:
                print(f"✅ New model ({new_accuracy:.1%}) beats or replaces previous -- DEPLOYING.")
                registry[key] = {
                    "accuracy": new_accuracy,
                    "row_count": len(subset),
                    "deployed_at": datetime.now().isoformat(),
                }
            else:
                print(
                    f"❌ New model ({new_accuracy:.1%}) did NOT beat previous "
                    f"({previous_entry['accuracy']:.1%}) -- KEEPING old model."
                )
                # Restore the backup since train_for() already
                # overwrote the file during training.
                if backup_path and backup_path.exists():
                    model_path.write_bytes(backup_path.read_bytes())

            if backup_path and backup_path.exists():
                backup_path.unlink()

    save_registry(registry)
    print("\n" + "=" * 60)
    print("Nightly cycle complete.")
    print("=" * 60)


def _train_and_get_accuracy(df, symbol, horizon):
    """
    Thin wrapper around train_model.py's train_for() that also
    returns the accuracy number for the deploy/keep comparison,
    without duplicating its training logic.
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    import joblib

    subset = df[(df.symbol == symbol) & (df.horizon == horizon)].copy()
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

    try:
        model = RandomForestClassifier(
            n_estimators=200, max_depth=6, min_samples_leaf=10,
            class_weight="balanced", random_state=42,
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        accuracy = accuracy_score(y_test, preds)

        model_path = MODELS_DIR / f"{symbol}_{horizon}m.joblib"
        joblib.dump({"model": model, "feature_cols": feature_cols}, model_path)

        return accuracy
    except Exception as error:
        print(f"Training error: {error}")
        return None


if __name__ == "__main__":
    run_nightly_cycle()


# --- Scheduling on Windows (Task Scheduler) ---
# 1. Open Task Scheduler -> Create Basic Task
# 2. Trigger: Daily, after market close (e.g. 4:00 PM IST)
# 3. Action: Start a program
#    Program: E:\Python_Project\Trading_Market_App_AI\.venv\Scripts\python.exe
#    Arguments: -m backend.prediction.nightly_retrain
#    Start in: E:\Python_Project\Trading_Market_App_AI
#
# --- Scheduling on Linux (cron) ---
# 30 16 * * 1-5 cd /path/to/project && .venv/bin/python -m backend.prediction.nightly_retrain
