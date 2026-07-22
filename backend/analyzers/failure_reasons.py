"""
Failure Reason Engine

Every brain in this system already stores prediction/outcome
(correct or wrong). This module adds the missing piece: WHEN a
prediction was wrong, WHY -- as structured, queryable tags, not a
guess after the fact. The tags are computed from the exact market
context captured AT PREDICTION TIME (not reconstructed later), so
"resistance was nearby" means it genuinely was, not an approximation.

This is what lets you eventually query real patterns like:
"BUY calls near resistance with high volatility fail X% of the time"
-- see failure_reason_stats() in database.py for that query.

HONEST LIMITATIONS, stated plainly:
- "High volatility" here is a proxy using ATR relative to price, NOT
  a real India VIX index feed. If you want the actual VIX, that's a
  separate data source to wire in later -- don't confuse this proxy
  for the real thing when reading tags.
- News sentiment is the same keyword-based scoring from
  news_ingestor.py, not a trained sentiment model -- treat
  "NEGATIVE_NEWS" as directional signal, not gospel.
- These tags are DESCRIPTIVE (what conditions were present), not yet
  a trained model that predicts failure probability from them. That's
  the natural next step once enough tagged failures accumulate --
  see failure_reason_stats() for the query that makes it possible.
"""

from __future__ import annotations


def compute_failure_reasons(direction: str, context: dict) -> list[str]:
    """
    context: the same feature snapshot already captured for this
    prediction (rsi, atr, price, support, resistance, regime,
    options bias, news_score, etc.) -- see the context dict built in
    market_service.py's _build_brain_call_context().

    Returns a list of reason tags. Empty list = no obvious
    contributing condition detected (also a meaningful, honest
    result -- not every loss has an identifiable cause here).
    """

    reasons = []

    price = context.get("price")
    support = context.get("support")
    resistance = context.get("resistance")
    atr = context.get("atr")
    regime = context.get("regime")
    options_bias = context.get("options_bias")
    news_score = context.get("news_score")
    rsi = context.get("rsi")

    # --- Proximity to support/resistance ---
    if price and resistance and atr:
        distance_to_resistance = resistance - price
        if direction == "UP" and 0 <= distance_to_resistance <= atr * 1.5:
            reasons.append("NEAR_RESISTANCE")

    if price and support and atr:
        distance_to_support = price - support
        if direction == "DOWN" and 0 <= distance_to_support <= atr * 1.5:
            reasons.append("NEAR_SUPPORT")

    # --- Volatility proxy (ATR relative to price -- NOT real VIX) ---
    if price and atr:
        atr_pct = (atr / price) * 100
        if atr_pct > 0.35:
            reasons.append("HIGH_VOLATILITY_PROXY")
        elif atr_pct < 0.08:
            reasons.append("LOW_VOLATILITY_CHOP")

    # --- Trend alignment ---
    if regime == "RANGING":
        reasons.append("WEAK_TREND_RANGING_MARKET")
    if regime == "TRENDING_DOWN" and direction == "UP":
        reasons.append("COUNTER_TREND_CALL")
    if regime == "TRENDING_UP" and direction == "DOWN":
        reasons.append("COUNTER_TREND_CALL")

    # --- Options positioning against the call ---
    if options_bias == "BEARISH" and direction == "UP":
        reasons.append("OPTIONS_FLOW_AGAINST_CALL")
    if options_bias == "BULLISH" and direction == "DOWN":
        reasons.append("OPTIONS_FLOW_AGAINST_CALL")

    # --- News sentiment against the call ---
    if news_score is not None:
        if news_score < -0.2 and direction == "UP":
            reasons.append("NEGATIVE_NEWS")
        if news_score > 0.2 and direction == "DOWN":
            reasons.append("POSITIVE_NEWS_AGAINST_SHORT")

    # --- Overbought/oversold against the call ---
    if rsi is not None:
        if rsi > 70 and direction == "UP":
            reasons.append("RSI_OVERBOUGHT")
        if rsi < 30 and direction == "DOWN":
            reasons.append("RSI_OVERSOLD")

    return reasons
