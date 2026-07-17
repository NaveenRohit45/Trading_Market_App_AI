"""
ML Predictor — Phase 3 inference

Loads whatever models train_model.py has produced (models/*.joblib)
and, if one exists for a given symbol+horizon, returns its prediction
alongside the existing V1 heuristic -- WITHOUT replacing it. This lets
you watch both side by side before trusting the ML output.

If no trained model exists yet for a symbol+horizon (very likely at
first), this quietly returns None and the app keeps behaving exactly
as it does today.
"""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

import pandas as pd
import joblib

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"


@lru_cache(maxsize=None)
def _load_model(symbol: str, horizon: int):
    path = MODELS_DIR / f"{symbol}_{horizon}m.joblib"

    if not path.exists():
        return None

    try:
        return joblib.load(path)
    except Exception as error:
        print(f"⚠️ Failed to load ML model {path}: {error}")
        return None


def predict_ml(symbol: str, horizon: int, analysis: dict, peer_analysis: dict, news_score: float):
    """
    Returns {"direction": ..., "confidence": ..., "probabilities": {...}}
    or None if no trained model exists yet for this symbol+horizon.
    """

    bundle = _load_model(symbol, horizon)

    if bundle is None:
        return None

    model = bundle["model"]
    feature_cols = bundle["feature_cols"]

    row = {
        "rsi": analysis.get("rsi"),
        "ema_fast": analysis.get("ema_fast"),
        "ema_slow": analysis.get("ema_slow"),
        "atr": analysis.get("atr"),
        "momentum": analysis.get("momentum"),
        "support": analysis.get("support"),
        "resistance": analysis.get("resistance"),
        "news_score": news_score,
        f"state_{analysis.get('state')}": 1,
        f"regime_{analysis.get('regime')}": 1,
        f"breakout_{analysis.get('breakout')}": 1,
        f"peer_state_{peer_analysis.get('state')}": 1,
    }

    X = pd.DataFrame([row])

    # Add any missing columns the model expects (from training-time
    # one-hot encoding) as 0, and drop anything extra.
    for col in feature_cols:
        if col not in X.columns:
            X[col] = 0

    X = X[feature_cols].fillna(0)

    try:
        proba = model.predict_proba(X)[0]
        classes = model.classes_
    except Exception as error:
        print(f"⚠️ ML prediction failed for {symbol} {horizon}m: {error}")
        return None

    probs = {cls: round(float(p) * 100, 1) for cls, p in zip(classes, proba)}
    direction = max(probs, key=probs.get)
    confidence = probs[direction]

    return {
        "horizon": horizon,
        "probabilities": probs,
        "direction": direction,
        "confidence": confidence,
        "source": "ML_V2",
    }
