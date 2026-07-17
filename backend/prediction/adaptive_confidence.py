"""
Adaptive Confidence Engine

This is the piece that turns a collection of independent brains into
an actually-adaptive system. Instead of fixed weights, each brain's
influence on the final verdict is scaled by ITS OWN recent real
accuracy (from database.brain_accuracy()), optionally conditioned on
the current market regime.

How it works, plainly:
1. Every brain (V1 heuristic, price-action, ML/RandomForest,
   LSTM, RL) casts a directional vote with its own confidence.
2. Each brain's vote is weighted by:
     weight = recent_accuracy * regime_relevance * base_confidence
   New/unproven brains (no resolved history yet) get a conservative
   default weight rather than 0 or full trust -- they need to EARN
   more influence over time.
3. Votes are combined into a final probability distribution over
   UP/DOWN/SIDEWAYS, and that's the adaptive verdict.
4. Crucially: DL and RL are ADDITIONAL votes here, not replacements
   for the V1 heuristic. If they don't have trained models yet, they
   simply don't vote -- nothing breaks.

This does NOT guarantee good predictions. It guarantees the SYSTEM'S
OWN CONFIDENCE reflects what has actually been working recently,
instead of a static guess made once at build time.
"""

from __future__ import annotations

from backend.prediction.regime_detector import detect_regime

DEFAULT_WEIGHT_UNPROVEN = 0.4    # brains with <20 resolved calls: capped trust
MIN_SAMPLE_FOR_FULL_TRUST = 30   # below this, blend toward the default weight


def _brain_weight(brain_name: str, accuracy_stats: dict) -> float:
    stats = accuracy_stats.get(brain_name)

    if not stats or stats.get("accuracy") is None:
        return DEFAULT_WEIGHT_UNPROVEN

    accuracy = stats["accuracy"] / 100.0
    sample_size = stats["sample_size"]

    # Blend toward the proven accuracy as sample size grows, so 3
    # lucky calls in a row can't swing the weight to 1.0 immediately.
    confidence_in_estimate = min(sample_size / MIN_SAMPLE_FOR_FULL_TRUST, 1.0)

    weight = (
        confidence_in_estimate * accuracy
        + (1 - confidence_in_estimate) * DEFAULT_WEIGHT_UNPROVEN
    )

    return max(0.05, weight)  # never fully zero out a brain -- it can recover


def combine_adaptive_verdict(
    symbol: str,
    analysis: dict,
    brain_votes: dict,
    db,
) -> dict:
    """
    brain_votes: {
        "price_action": {"direction": "UP", "confidence": 70.5},
        "v1_heuristic":  {"direction": "UP", "confidence": 55.0},
        "ml_model":      {"direction": "SIDEWAYS", "confidence": 48.0},   # optional
        "lstm_model":    {"direction": "UP", "confidence": 61.0},        # optional
        ...
    }
    Missing/None entries are simply skipped -- this works fine with
    only the brains you actually have running.
    """

    regime = detect_regime(analysis)

    accuracy_stats = db.brain_accuracy(symbol=symbol, regime=regime, lookback=100)

    # Fall back to regime-agnostic accuracy if there's no history yet
    # for this specific regime (common early on -- not enough data
    # sliced this finely).
    fallback_stats = db.brain_accuracy(symbol=symbol, lookback=100)

    scores = {"UP": 0.0, "DOWN": 0.0, "SIDEWAYS": 0.0}
    weights_used = {}

    for brain_name, vote in brain_votes.items():
        if not vote or not vote.get("direction"):
            continue

        stats = accuracy_stats.get(brain_name) or fallback_stats.get(brain_name)
        weight = _brain_weight(brain_name, {brain_name: stats} if stats else {})

        confidence = (vote.get("confidence") or 50.0) / 100.0

        contribution = weight * confidence
        scores[vote["direction"]] = scores.get(vote["direction"], 0.0) + contribution
        weights_used[brain_name] = round(weight, 3)

    total = sum(scores.values()) or 1e-8
    probabilities = {k: round(v / total * 100, 1) for k, v in scores.items()}

    verdict_direction = max(probabilities, key=probabilities.get)
    verdict_confidence = probabilities[verdict_direction]

    # Don't call a trade when the vote is genuinely split -- this is
    # the same spirit as your existing "NO-TRADE" verdict logic.
    is_conflicted = (
        max(probabilities.values()) - sorted(probabilities.values())[-2] < 10
    )

    return {
        "symbol": symbol,
        "regime": regime,
        "direction": "NO-TRADE" if is_conflicted else verdict_direction,
        "confidence": verdict_confidence,
        "probabilities": probabilities,
        "brain_weights": weights_used,
        "conflicted": is_conflicted,
    }
