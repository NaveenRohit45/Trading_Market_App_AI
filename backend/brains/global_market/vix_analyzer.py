"""
============================================================
India VIX Analyzer
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Analyzes India VIX (Volatility Index).

India VIX measures market fear and expected
volatility.

This analyzer does NOT predict direction.

Higher VIX
    → Higher Risk

Lower VIX
    → Stable Market

Returns

VIXAnalysis
"""

from __future__ import annotations

from .models import (
    VIXAnalysis,
    VIXLevel,
)


class VIXAnalyzer:

    @staticmethod
    def analyze(
        vix_value: float,
    ) -> VIXAnalysis:

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if vix_value < 0:

            raise ValueError(
                "VIX value cannot be negative."
            )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if vix_value < 12:

            level = VIXLevel.LOW

            score = 90

            reason = (
                "Very low volatility. Stable market conditions."
            )

        elif vix_value < 18:

            level = VIXLevel.NORMAL

            score = 75

            reason = (
                "Normal market volatility."
            )

        elif vix_value < 25:

            level = VIXLevel.HIGH

            score = 40

            reason = (
                "High volatility. Trade with caution."
            )

        else:

            level = VIXLevel.PANIC

            score = 10

            reason = (
                "Extreme fear in the market."
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return VIXAnalysis(

            level=level,

            value=round(
                vix_value,
                2,
            ),

            score=score,

            reason=reason,

        )