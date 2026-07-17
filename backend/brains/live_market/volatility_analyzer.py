"""
============================================================
Live Market Brain
Volatility Analyzer
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from .models import VolatilityLevel


# ============================================================
# Result Model
# ============================================================

@dataclass(slots=True)
class VolatilityAnalysis:
    """
    Result produced by Volatility Analyzer.
    """

    level: VolatilityLevel
    average_range: float
    max_range: float
    min_range: float
    volatility_score: float
    reason: str


# ============================================================
# Analyzer
# ============================================================

class VolatilityAnalyzer:
    """
    Measures market volatility using candle ranges.

    Formula

    Candle Range = High - Low

    Average Range = Average of last N candle ranges

    Volatility Score = Average Range / Current Price * 100
    """

    LOW_THRESHOLD = 0.15
    NORMAL_THRESHOLD = 0.40
    HIGH_THRESHOLD = 0.80

    @classmethod
    def analyze(cls, candles: Sequence) -> VolatilityAnalysis:
        """
        Parameters
        ----------
        candles
            Sequence of candle objects.

            Each candle must expose:

            candle.high
            candle.low
            candle.close
        """

        if len(candles) < 2:
            return cls.unavailable(
                "Waiting for at least two candles."
            )

        ranges = [
            candle.high - candle.low
            for candle in candles
        ]

        avg_range = mean(ranges)

        current_price = candles[-1].close

        volatility_score = (
            avg_range / current_price
        ) * 100

        if volatility_score < cls.LOW_THRESHOLD:

            level = VolatilityLevel.LOW
            reason = "Very small candle ranges."

        elif volatility_score < cls.NORMAL_THRESHOLD:

            level = VolatilityLevel.NORMAL
            reason = "Healthy market volatility."

        elif volatility_score < cls.HIGH_THRESHOLD:

            level = VolatilityLevel.HIGH
            reason = "Large candle ranges detected."

        else:

            level = VolatilityLevel.EXTREME
            reason = "Extreme price movement detected."

        return VolatilityAnalysis(
            level=level,
            average_range=round(avg_range, 2),
            max_range=round(max(ranges), 2),
            min_range=round(min(ranges), 2),
            volatility_score=round(volatility_score, 2),
            reason=reason,
        )

    # ============================================================
    # Unavailable
    # ============================================================

    @classmethod
    def unavailable(
        cls,
        reason: str = "Waiting for enough candles.",
    ) -> VolatilityAnalysis:

        return VolatilityAnalysis(
            level=VolatilityLevel.LOW,
            average_range=0.0,
            max_range=0.0,
            min_range=0.0,
            volatility_score=0.0,
            reason=reason,
        )