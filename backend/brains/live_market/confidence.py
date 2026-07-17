"""
============================================================
Trading Market AI
Confidence Engine
Author : Super Cat
============================================================

Calculates confidence based on agreement between
all market analyzers.

This module does NOT predict market direction.

It only measures confidence in the prediction.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import MarketBias


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class ConfidenceResult:

    confidence: float

    confidence_level: str

    agreement_score: float

    reasons: list[str]


# ============================================================
# Confidence Engine
# ============================================================

class ConfidenceEngine:

    @classmethod
    def calculate(

        cls,

        trend,

        strength,

        liquidity,

        volatility,

        gap,

        session,

        expiry,

        strategy,

    ) -> ConfidenceResult:

        confidence = 50.0

        reasons = []

        # ---------------------------------------------------
        # Trend
        # ---------------------------------------------------

        confidence += (trend.trend_score - 50) * 0.30

        reasons.append(trend.reason)

        # ---------------------------------------------------
        # Market Strength
        # ---------------------------------------------------

        confidence += (strength.score - 50) * 0.20

        reasons.append(strength.reason)

        # ---------------------------------------------------
        # Liquidity
        # ---------------------------------------------------

        confidence += (liquidity.liquidity_score - 50) * 0.15

        reasons.append(liquidity.reason)

        # ---------------------------------------------------
        # Volatility
        # ---------------------------------------------------

        if volatility.level.name == "NORMAL":

            confidence += 8

        elif volatility.level.name == "HIGH":

            confidence += 5

        elif volatility.level.name == "LOW":

            confidence -= 8

        elif volatility.level.name == "EXTREME":

            confidence -= 15

        reasons.append(volatility.reason)

        # ---------------------------------------------------
        # Gap
        # ---------------------------------------------------

        if gap.is_gap_significant:

            confidence += 4

        reasons.append(gap.reason)

        # ---------------------------------------------------
        # Session
        # ---------------------------------------------------

        if session.session.name == "OPENING":

            confidence -= 5

        elif session.session.name == "MORNING":

            confidence += 5

        elif session.session.name == "MIDDAY":

            confidence -= 8

        elif session.session.name == "AFTERNOON":

            confidence += 2

        elif session.session.name == "CLOSING":

            confidence += 3

        reasons.append(session.reason)

        # ---------------------------------------------------
        # Expiry
        # ---------------------------------------------------

        if expiry.is_expiry_day:

            confidence -= 10

        reasons.append(expiry.reason)

        # ---------------------------------------------------
        # Strategy
        # ---------------------------------------------------

        confidence += strategy.confidence_modifier

        reasons.append(strategy.reason)

        # ---------------------------------------------------
        # Agreement Bonus
        # ---------------------------------------------------

        agreement = 0

        if trend.bias == MarketBias.BULLISH:

            if strength.score > 70:
                agreement += 10

            if liquidity.level.name == "HIGH":
                agreement += 5

        elif trend.bias == MarketBias.BEARISH:

            if strength.score < 35:
                agreement += 10

            if liquidity.level.name == "HIGH":
                agreement += 5

        confidence += agreement

        confidence = max(0, min(confidence, 100))

        # ---------------------------------------------------
        # Level
        # ---------------------------------------------------

        if confidence >= 90:

            level = "VERY_HIGH"

        elif confidence >= 75:

            level = "HIGH"

        elif confidence >= 60:

            level = "MEDIUM"

        elif confidence >= 40:

            level = "LOW"

        else:

            level = "VERY_LOW"

        return ConfidenceResult(

            confidence=round(confidence, 2),

            confidence_level=level,

            agreement_score=agreement,

            reasons=reasons,

        )