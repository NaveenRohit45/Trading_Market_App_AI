"""
============================================================
Live Market Brain
Trend Analyzer
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from .models import MarketBias, MarketTrend


# ============================================================
# Result Model
# ============================================================

@dataclass(slots=True)
class TrendAnalysis:
    """
    Result produced by Trend Analyzer.
    """

    trend: MarketTrend
    bias: MarketBias

    trend_score: float

    ema9: float
    ema21: float

    higher_highs: int
    higher_lows: int
    lower_highs: int
    lower_lows: int

    reason: str


# ============================================================
# Analyzer
# ============================================================

class TrendAnalyzer:

    EMA_FAST = 3
    EMA_SLOW = 5

    @classmethod
    def analyze(cls, candles: Sequence):

        if len(candles) < cls.EMA_SLOW:
            return cls.unavailable(
                f"Waiting for {cls.EMA_SLOW} candles."
            )

        closes = [c.close for c in candles]

        ema9 = cls._ema(closes, cls.EMA_FAST)
        ema21 = cls._ema(closes, cls.EMA_SLOW)

        hh = 0
        hl = 0
        lh = 0
        ll = 0

        for i in range(1, len(candles)):

            prev = candles[i - 1]
            curr = candles[i]

            if curr.high > prev.high:
                hh += 1
            else:
                lh += 1

            if curr.low > prev.low:
                hl += 1
            else:
                ll += 1

        score = 50

        # EMA Trend
        if ema9 > ema21:
            score += 20
        else:
            score -= 20

        # Current Price
        if closes[-1] > ema9:
            score += 10
        else:
            score -= 10

        # Market Structure
        score += (hh - lh) * 2
        score += (hl - ll) * 2

        score = max(0, min(score, 100))

        # Classification

        if score >= 85:

            trend = MarketTrend.STRONG_UPTREND
            bias = MarketBias.STRONG_BULLISH

        elif score >= 65:

            trend = MarketTrend.UPTREND
            bias = MarketBias.BULLISH

        elif score <= 15:

            trend = MarketTrend.STRONG_DOWNTREND
            bias = MarketBias.STRONG_BEARISH

        elif score <= 35:

            trend = MarketTrend.DOWNTREND
            bias = MarketBias.BEARISH

        else:

            trend = MarketTrend.SIDEWAYS
            bias = MarketBias.NEUTRAL

        return TrendAnalysis(

            trend=trend,
            bias=bias,

            trend_score=round(score, 2),

            ema9=round(ema9, 2),
            ema21=round(ema21, 2),

            higher_highs=hh,
            higher_lows=hl,
            lower_highs=lh,
            lower_lows=ll,

            reason=cls._reason(score),
        )

    # --------------------------------------------------------

    @staticmethod
    def _ema(values, period):

        multiplier = 2 / (period + 1)

        ema = mean(values[:period])

        for value in values[period:]:

            ema = (
                (value - ema)
                * multiplier
            ) + ema

        return ema

    # --------------------------------------------------------

    @staticmethod
    def _reason(score):

        if score >= 85:
            return "Strong bullish trend confirmed."

        if score >= 65:
            return "Bullish trend confirmed."

        if score <= 15:
            return "Strong bearish trend confirmed."

        if score <= 35:
            return "Bearish trend confirmed."

        return "Market moving sideways."

    # ============================================================
    # Unavailable
    # ============================================================

    @classmethod
    def unavailable(
        cls,
        reason: str = "Trend data unavailable.",
    ) -> TrendAnalysis:

        return TrendAnalysis(

            trend=MarketTrend.SIDEWAYS,

            bias=MarketBias.NEUTRAL,

            trend_score=0.0,

            ema9=0.0,

            ema21=0.0,

            higher_highs=0,

            higher_lows=0,

            lower_highs=0,

            lower_lows=0,

            reason=reason,

        )