"""
Candlestick Pattern Detector

HOW "TEACHING THE AI" A CHEAT SHEET ACTUALLY WORKS: an image or PDF
of pattern shapes can't be fed into a trading model directly -- there
is no learning step here. What this module does instead is the real
equivalent: it encodes each pattern's textbook DEFINITION (body size
relative to range, wick length ratios, relationship between
consecutive candles' opens/closes) as executable rules, run directly
against your actual OHLC data. This is how professional charting
platforms detect these patterns too -- deterministic geometry, not a
trained model. It is exact and reliable for what it does, but it is
not "intelligence" -- it's pattern-matching against textbook shapes.

Where this actually adds value in THIS system: a detected pattern
becomes one more vote for the Adaptive Confidence Engine, and gets
cited by name in the Real AI (Claude) reasoning layer -- so instead
of Claude vaguely saying "momentum looks bullish," it can say
"Bullish Engulfing formed on the 5m chart," a specific, checkable
claim.

HONEST LIMITATION: candlestick patterns are widely used but have
mixed academic support for real predictive edge, especially in
isolation. Same rule as every other brain in this system: it votes,
and the Adaptive Confidence Engine tracks whether ITS calls are
actually right often enough to deserve trust -- these patterns are
not assumed to work just because they're named and well-known.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DetectedPattern:
    name: str
    bias: str          # "BULLISH" | "BEARISH" | "NEUTRAL"
    candles_used: int  # 1, 2, or 3
    strength: float    # 0-100, rough confidence based on shape clarity


def _body(c) -> float:
    return abs(c.close - c.open)


def _range(c) -> float:
    return max(c.high - c.low, 1e-9)


def _upper_wick(c) -> float:
    return c.high - max(c.open, c.close)


def _lower_wick(c) -> float:
    return min(c.open, c.close) - c.low


def _is_bullish(c) -> bool:
    return c.close > c.open


def _is_bearish(c) -> bool:
    return c.close < c.open


def _body_ratio(c) -> float:
    return _body(c) / _range(c)


# ==========================================================
# Single-candle patterns
# ==========================================================

def _detect_single(c) -> list[DetectedPattern]:
    found = []
    body_ratio = _body_ratio(c)
    upper = _upper_wick(c)
    lower = _lower_wick(c)
    rng = _range(c)

    # Doji family: body is a tiny fraction of the range.
    if body_ratio < 0.08:
        if lower > rng * 0.6 and upper < rng * 0.15:
            found.append(DetectedPattern("Dragonfly Doji", "BULLISH", 1, 65))
        elif upper > rng * 0.6 and lower < rng * 0.15:
            found.append(DetectedPattern("Gravestone Doji", "BEARISH", 1, 65))
        elif upper > rng * 0.35 and lower > rng * 0.35:
            found.append(DetectedPattern("Long-Legged Doji", "NEUTRAL", 1, 50))
        else:
            found.append(DetectedPattern("Doji", "NEUTRAL", 1, 50))
        return found

    # Marubozu: body fills almost the whole range, minimal wicks.
    if body_ratio > 0.92:
        if _is_bullish(c):
            found.append(DetectedPattern("Bullish Marubozu", "BULLISH", 1, 75))
        else:
            found.append(DetectedPattern("Bearish Marubozu", "BEARISH", 1, 75))
        return found

    # Hammer / Hanging Man: small body near the top, long lower wick,
    # minimal upper wick. Direction meaning depends on prior trend,
    # which the caller supplies via `prior_trend`.
    if lower > _body(c) * 2 and upper < _body(c) * 0.5 and body_ratio < 0.35:
        found.append(DetectedPattern("Hammer/Hanging Man shape", "CONTEXT", 1, 60))

    # Inverted Hammer / Shooting Star: small body near the bottom,
    # long upper wick, minimal lower wick.
    if upper > _body(c) * 2 and lower < _body(c) * 0.5 and body_ratio < 0.35:
        found.append(DetectedPattern("Inverted Hammer/Shooting Star shape", "CONTEXT", 1, 60))

    # Spinning top: small-ish body, both wicks meaningful and roughly balanced.
    if 0.1 <= body_ratio <= 0.35 and upper > rng * 0.2 and lower > rng * 0.2:
        bias = "BULLISH" if _is_bullish(c) else "BEARISH"
        found.append(DetectedPattern(f"{bias.title()} Spinning Top", "NEUTRAL", 1, 45))

    return found


def _resolve_context_pattern(pattern_name: str, prior_trend: str) -> DetectedPattern | None:
    """
    Hammer/Shooting Star shapes mean opposite things depending on
    whether they appear after a downtrend or an uptrend -- this
    resolves that using the trend context the caller provides
    (e.g. from your existing regime detector).
    """
    if pattern_name == "Hammer/Hanging Man shape":
        if prior_trend == "TRENDING_DOWN":
            return DetectedPattern("Hammer", "BULLISH", 1, 65)
        if prior_trend == "TRENDING_UP":
            return DetectedPattern("Hanging Man", "BEARISH", 1, 55)
    if pattern_name == "Inverted Hammer/Shooting Star shape":
        if prior_trend == "TRENDING_DOWN":
            return DetectedPattern("Inverted Hammer", "BULLISH", 1, 55)
        if prior_trend == "TRENDING_UP":
            return DetectedPattern("Shooting Star", "BEARISH", 1, 65)
    return None


# ==========================================================
# Two-candle patterns
# ==========================================================

def _detect_double(prev, cur) -> list[DetectedPattern]:
    found = []

    prev_bull, prev_bear = _is_bullish(prev), _is_bearish(prev)
    cur_bull, cur_bear = _is_bullish(cur), _is_bearish(cur)

    # Engulfing: current body fully engulfs previous body, opposite direction.
    if cur_bull and prev_bear and cur.close > prev.open and cur.open < prev.close:
        found.append(DetectedPattern("Bullish Engulfing", "BULLISH", 2, 75))
    elif cur_bear and prev_bull and cur.close < prev.open and cur.open > prev.close:
        found.append(DetectedPattern("Bearish Engulfing", "BEARISH", 2, 75))

    # Harami: current body fully inside previous body, opposite-ish direction.
    elif (
        _body(cur) < _body(prev) * 0.7
        and max(cur.open, cur.close) < max(prev.open, prev.close)
        and min(cur.open, cur.close) > min(prev.open, prev.close)
    ):
        if prev_bear and cur_bull:
            found.append(DetectedPattern("Bullish Harami", "BULLISH", 2, 60))
        elif prev_bull and cur_bear:
            found.append(DetectedPattern("Bearish Harami", "BEARISH", 2, 60))

    # Kicker: strong gap in opposite direction between two marubozu-like candles.
    if prev_bear and cur_bull and cur.open >= prev.open and _body_ratio(prev) > 0.6 and _body_ratio(cur) > 0.6:
        found.append(DetectedPattern("Bullish Kicker", "BULLISH", 2, 70))
    elif prev_bull and cur_bear and cur.open <= prev.open and _body_ratio(prev) > 0.6 and _body_ratio(cur) > 0.6:
        found.append(DetectedPattern("Bearish Kicker", "BEARISH", 2, 70))

    # Piercing Line: bearish candle followed by a bullish candle that
    # closes above the midpoint of the prior body.
    prev_mid = (prev.open + prev.close) / 2
    if prev_bear and cur_bull and cur.open < prev.close and cur.close > prev_mid and cur.close < prev.open:
        found.append(DetectedPattern("Piercing Line", "BULLISH", 2, 65))

    # Dark Cloud Cover: bullish candle followed by bearish candle
    # closing below the midpoint of the prior body.
    if prev_bull and cur_bear and cur.open > prev.close and cur.close < prev_mid and cur.close > prev.open:
        found.append(DetectedPattern("Dark Cloud Cover", "BEARISH", 2, 65))

    # Tweezer Top/Bottom: two candles with nearly identical highs (top)
    # or lows (bottom).
    if abs(prev.high - cur.high) / _range(prev) < 0.05 and prev_bull and cur_bear:
        found.append(DetectedPattern("Tweezer Top", "BEARISH", 2, 55))
    if abs(prev.low - cur.low) / _range(prev) < 0.05 and prev_bear and cur_bull:
        found.append(DetectedPattern("Tweezer Bottom", "BULLISH", 2, 55))

    return found


# ==========================================================
# Three-candle patterns
# ==========================================================

def _detect_triple(c1, c2, c3) -> list[DetectedPattern]:
    found = []

    c1_bear, c1_bull = _is_bearish(c1), _is_bullish(c1)
    c3_bull, c3_bear = _is_bullish(c3), _is_bearish(c3)
    c1_mid = (c1.open + c1.close) / 2

    # Morning Star: bearish, small-bodied middle candle (gap down), strong bullish close.
    if (
        c1_bear and _body_ratio(c1) > 0.5
        and _body_ratio(c2) < 0.35
        and c3_bull and c3.close > c1_mid
    ):
        if _body_ratio(c2) < 0.1:
            found.append(DetectedPattern("Morning Doji Star", "BULLISH", 3, 75))
        else:
            found.append(DetectedPattern("Morning Star", "BULLISH", 3, 75))

    # Evening Star: bullish, small-bodied middle candle, strong bearish close.
    if (
        c1_bull and _body_ratio(c1) > 0.5
        and _body_ratio(c2) < 0.35
        and c3_bear and c3.close < c1_mid
    ):
        if _body_ratio(c2) < 0.1:
            found.append(DetectedPattern("Evening Doji Star", "BEARISH", 3, 75))
        else:
            found.append(DetectedPattern("Evening Star", "BEARISH", 3, 75))

    # Three White Soldiers: three consecutive strong bullish candles, each closing higher.
    if (
        c1_bull and c2 is not None and _is_bullish(c2) and c3_bull
        and c2.close > c1.close and c3.close > c2.close
        and _body_ratio(c1) > 0.5 and _body_ratio(c2) > 0.5 and _body_ratio(c3) > 0.5
    ):
        found.append(DetectedPattern("Three White Soldiers", "BULLISH", 3, 80))

    # Three Black Crows: three consecutive strong bearish candles, each closing lower.
    if (
        c1_bear and _is_bearish(c2) and c3_bear
        and c2.close < c1.close and c3.close < c2.close
        and _body_ratio(c1) > 0.5 and _body_ratio(c2) > 0.5 and _body_ratio(c3) > 0.5
    ):
        found.append(DetectedPattern("Three Black Crows", "BEARISH", 3, 80))

    # Three Inside Up/Down: Harami followed by confirmation candle.
    harami_up = (
        c1_bear and _is_bullish(c2)
        and max(c2.open, c2.close) < max(c1.open, c1.close)
        and min(c2.open, c2.close) > min(c1.open, c1.close)
    )
    harami_down = (
        c1_bull and _is_bearish(c2)
        and max(c2.open, c2.close) < max(c1.open, c1.close)
        and min(c2.open, c2.close) > min(c1.open, c1.close)
    )
    if harami_up and c3_bull and c3.close > c2.close:
        found.append(DetectedPattern("Three Inside Up", "BULLISH", 3, 70))
    if harami_down and c3_bear and c3.close < c2.close:
        found.append(DetectedPattern("Three Inside Down", "BEARISH", 3, 70))

    return found


def detect_patterns(candles: list, regime: str = "RANGING") -> list[DetectedPattern]:
    """
    Runs every pattern check against the most recent candles.
    `candles` should be oldest-first (same order CandleEngine.series()
    already returns). `regime` (e.g. from your existing regime
    detector) resolves context-dependent single-candle shapes like
    Hammer vs Hanging Man.

    Returns a list of DetectedPattern -- usually 0-2 patterns per
    call, since most candle combinations don't match anything.
    """

    if len(candles) < 1:
        return []

    results = []

    last = candles[-1]

    for pattern in _detect_single(last):
        if pattern.bias == "CONTEXT":
            resolved = _resolve_context_pattern(pattern.name, regime)
            if resolved:
                results.append(resolved)
        else:
            results.append(pattern)

    if len(candles) >= 2:
        results.extend(_detect_double(candles[-2], candles[-1]))

    if len(candles) >= 3:
        results.extend(_detect_triple(candles[-3], candles[-2], candles[-1]))

    return results


def summarize_bias(patterns: list[DetectedPattern]) -> dict:
    """
    Collapses multiple detected patterns into a single vote, the same
    shape every other brain uses ({"direction", "confidence"}) so this
    can plug directly into the Adaptive Confidence Engine.
    """

    if not patterns:
        return {"direction": "SIDEWAYS", "confidence": 40.0, "patterns": []}

    bullish = [p for p in patterns if p.bias == "BULLISH"]
    bearish = [p for p in patterns if p.bias == "BEARISH"]

    bull_strength = sum(p.strength for p in bullish)
    bear_strength = sum(p.strength for p in bearish)

    if bull_strength > bear_strength:
        direction = "UP"
        confidence = min(85.0, 50.0 + (bull_strength - bear_strength) / 4)
    elif bear_strength > bull_strength:
        direction = "DOWN"
        confidence = min(85.0, 50.0 + (bear_strength - bull_strength) / 4)
    else:
        direction = "SIDEWAYS"
        confidence = 45.0

    return {
        "direction": direction,
        "confidence": round(confidence, 1),
        "patterns": [{"name": p.name, "bias": p.bias, "strength": p.strength} for p in patterns],
    }
