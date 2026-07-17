"""
Market Regime Detector

Classifies the current market into one of:
  TRENDING_UP, TRENDING_DOWN, RANGING, HIGH_VOLATILITY, LOW_VOLATILITY

Uses the same indicators the analyzers already compute (EMA spread for
trend direction/strength, ATR relative to price for volatility) --
deliberately simple and explainable rather than a black box, because
this classification feeds into WHY the Confidence Engine trusts or
distrusts each brain, and that reasoning needs to stay inspectable.
"""

from __future__ import annotations


def detect_regime(analysis: dict) -> str:
    """
    analysis: the same per-symbol dict your analyzers already produce
    (rsi, ema_fast, ema_slow, atr, price, momentum, ...).
    """

    price = analysis.get("price") or 0
    atr = analysis.get("atr") or 0
    ema_fast = analysis.get("ema_fast")
    ema_slow = analysis.get("ema_slow")
    momentum = analysis.get("momentum") or 0

    if not price:
        return "UNKNOWN"

    atr_pct = (atr / price) * 100 if price else 0

    # Volatility regime takes priority -- a high-vol trending market
    # behaves very differently from a calm trending one, and brains
    # tuned for one often misfire in the other.
    if atr_pct > 0.35:
        return "HIGH_VOLATILITY"

    if atr_pct < 0.08:
        return "LOW_VOLATILITY"

    # Trend regime: EMA spread + momentum direction agreement.
    if ema_fast is not None and ema_slow is not None:
        ema_spread_pct = ((ema_fast - ema_slow) / ema_slow) * 100 if ema_slow else 0

        if ema_spread_pct > 0.05 and momentum > 0:
            return "TRENDING_UP"

        if ema_spread_pct < -0.05 and momentum < 0:
            return "TRENDING_DOWN"

    return "RANGING"
