"""
============================================================
Live Market Brain
Market Strength Analyzer
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import MarketStrength


# ============================================================
# Result Model
# ============================================================

@dataclass(slots=True)
class MarketStrengthAnalysis:
    """
    Result produced by Market Strength Analyzer.
    """

    strength: MarketStrength

    score: float

    nifty_change: float
    sensex_change: float
    banknifty_change: float

    advance_decline_ratio: float

    reason: str


# ============================================================
# Analyzer
# ============================================================

class MarketStrengthAnalyzer:
    """
    Determines the overall strength of the market.

    Inputs
    ------
    - NIFTY % Change
    - SENSEX % Change
    - BANK NIFTY % Change
    - Advance / Decline Ratio
    """

    @classmethod
    def analyze(
        cls,
        nifty_change: float,
        sensex_change: float,
        banknifty_change: float,
        advance_decline_ratio: float,
    ) -> MarketStrengthAnalysis:

        score = 50.0

        # ----------------------------------------------------
        # NIFTY
        # ----------------------------------------------------

        score += nifty_change * 10

        # ----------------------------------------------------
        # SENSEX
        # ----------------------------------------------------

        score += sensex_change * 8

        # ----------------------------------------------------
        # BANK NIFTY
        # ----------------------------------------------------

        score += banknifty_change * 12

        # ----------------------------------------------------
        # Breadth
        # ----------------------------------------------------

        if advance_decline_ratio > 2.0:
            score += 15

        elif advance_decline_ratio > 1.2:
            score += 8

        elif advance_decline_ratio < 0.5:
            score -= 15

        elif advance_decline_ratio < 0.8:
            score -= 8

        # ----------------------------------------------------

        score = max(0.0, min(score, 100.0))

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        if score >= 85:

            strength = MarketStrength.VERY_STRONG

        elif score >= 70:

            strength = MarketStrength.STRONG

        elif score >= 45:

            strength = MarketStrength.MODERATE

        elif score >= 25:

            strength = MarketStrength.WEAK

        else:

            strength = MarketStrength.VERY_WEAK

        return MarketStrengthAnalysis(

            strength=strength,

            score=round(score, 2),

            nifty_change=round(nifty_change, 2),

            sensex_change=round(sensex_change, 2),

            banknifty_change=round(banknifty_change, 2),

            advance_decline_ratio=round(
                advance_decline_ratio,
                2,
            ),

            reason=cls._reason(strength),
        )

    # --------------------------------------------------------

    @staticmethod
    def _reason(strength: MarketStrength) -> str:

        reasons = {

            MarketStrength.VERY_STRONG:
                "Broad market participation with strong momentum.",

            MarketStrength.STRONG:
                "Market showing healthy bullish participation.",

            MarketStrength.MODERATE:
                "Market participation is balanced.",

            MarketStrength.WEAK:
                "Weak market participation detected.",

            MarketStrength.VERY_WEAK:
                "Very weak market with broad selling pressure.",
        }

        return reasons[strength]

    @classmethod
    def unavailable(cls):

        return MarketStrengthAnalysis(

            strength=MarketStrength.MODERATE,

            score=50,

            nifty_change=0,

            sensex_change=0,

            banknifty_change=0,

            advance_decline_ratio=1,

            reason="Market strength data unavailable.",

        )