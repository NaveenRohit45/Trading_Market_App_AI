"""
============================================================
Live Market Brain
Liquidity Analyzer
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import LiquidityLevel


# ============================================================
# Result Model
# ============================================================

@dataclass(slots=True)
class LiquidityAnalysis:
    """
    Result produced by Liquidity Analyzer.
    """

    level: LiquidityLevel

    current_volume: float
    average_volume: float

    volume_ratio: float

    tick_rate: float

    liquidity_score: float

    reason: str


# ============================================================
# Analyzer
# ============================================================

class LiquidityAnalyzer:
    """
    Measures market liquidity using

    - Current Volume
    - Average Volume
    - Tick Frequency

    Liquidity Score

        70% -> Volume Ratio
        30% -> Tick Activity
    """

    LOW_THRESHOLD = 40
    NORMAL_THRESHOLD = 70

    @classmethod
    def analyze(
        cls,
        current_volume: float,
        average_volume: float,
        tick_rate: float,
    ) -> LiquidityAnalysis:

        if average_volume <= 0:
            raise ValueError(
                "average_volume must be greater than zero."
            )

        volume_ratio = (
            current_volume / average_volume
        ) * 100

        # -----------------------------
        # Volume Score
        # -----------------------------

        volume_score = min(volume_ratio, 100)

        # -----------------------------
        # Tick Score
        # -----------------------------

        tick_score = min(tick_rate, 100)

        # -----------------------------
        # Final Liquidity Score
        # -----------------------------

        liquidity_score = (
            volume_score * 0.70
            +
            tick_score * 0.30
        )

        # -----------------------------
        # Classification
        # -----------------------------

        if liquidity_score < cls.LOW_THRESHOLD:

            level = LiquidityLevel.LOW

            reason = (
                "Low participation detected."
            )

        elif liquidity_score < cls.NORMAL_THRESHOLD:

            level = LiquidityLevel.NORMAL

            reason = (
                "Normal market participation."
            )

        else:

            level = LiquidityLevel.HIGH

            reason = (
                "High market participation."
            )

        return LiquidityAnalysis(

            level=level,

            current_volume=round(current_volume, 2),

            average_volume=round(average_volume, 2),

            volume_ratio=round(volume_ratio, 2),

            tick_rate=round(tick_rate, 2),

            liquidity_score=round(liquidity_score, 2),

            reason=reason,
        )

    @classmethod
    def unavailable(cls):

        return LiquidityAnalysis(

            level=LiquidityLevel.NORMAL,

            current_volume=0,

            average_volume=0,

            volume_ratio=0,

            tick_rate=0,

            liquidity_score=50,

            reason="Liquidity data unavailable.",

        )