"""
============================================================
Trading Market AI
Signal Fusion Engine
Author : Super Cat
============================================================

Combines all analyzer outputs into one unified market opinion.

Every analyzer contributes a weighted score.

The final score is used by

• Confidence Engine
• Trade Decision Engine
• Dashboard
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    MarketBias,
    RecommendedStrategy,
)


# ==========================================================
# Result
# ==========================================================

@dataclass(slots=True)
class FusionResult:

    market_score: float

    # confidence: float

    bias: MarketBias

    strategy: RecommendedStrategy

    reasons: list[str]

    warnings: list[str]


# ==========================================================
# Signal Fusion Engine
# ==========================================================

class SignalFusionEngine:

    """
    Every analyzer contributes to the final score.

    Trend            30%

    Market Strength  20%

    Liquidity        15%

    Volatility       10%

    Gap              10%

    Session          5%

    Expiry           10%
    """

    WEIGHTS = {

        "trend": 30,

        "strength": 20,

        "liquidity": 15,

        "volatility": 10,

        "gap": 10,

        "session": 5,

        "expiry": 10,

    }

    # -----------------------------------------------------

    @classmethod
    def fuse(

        cls,

        trend,

        strength,

        liquidity,

        volatility,

        gap,

        session,

        expiry,

    ) -> FusionResult:

        score = 0.0

        reasons = []

        warnings = []

        # ----------------------------------------------
        # Trend
        # ----------------------------------------------

        score += (

            trend.trend_score

            *

            cls.WEIGHTS["trend"]

        ) / 100

        reasons.append(trend.reason)

        # ----------------------------------------------
        # Market Strength
        # ----------------------------------------------

        score += (

            strength.score

            *

            cls.WEIGHTS["strength"]

        ) / 100

        reasons.append(strength.reason)

        # ----------------------------------------------
        # Liquidity
        # ----------------------------------------------

        score += (

            liquidity.liquidity_score

            *

            cls.WEIGHTS["liquidity"]

        ) / 100

        reasons.append(liquidity.reason)

        # ----------------------------------------------
        # Volatility
        # ----------------------------------------------

        volatility_score = {

            "LOW": 45,

            "NORMAL": 75,

            "HIGH": 90,

            "EXTREME": 60,

        }[volatility.level.name]

        score += (

            volatility_score

            *

            cls.WEIGHTS["volatility"]

        ) / 100

        reasons.append(volatility.reason)

        # ----------------------------------------------
        # Gap
        # ----------------------------------------------

        gap_score = {

            "GAP_UP": 80,

            "GAP_DOWN": 35,

            "FLAT": 60,

        }[gap.gap_type.name]

        score += (

            gap_score

            *

            cls.WEIGHTS["gap"]

        ) / 100

        reasons.append(gap.reason)

        # ----------------------------------------------
        # Session
        # ----------------------------------------------

        session_score = {

            "PRE_MARKET": 30,

            "OPENING": 90,

            "MORNING": 85,

            "MIDDAY": 50,

            "AFTERNOON": 75,

            "CLOSING": 70,

            "POST_MARKET": 20,

            "CLOSED": 0,

        }[session.session.name]

        score += (

            session_score

            *

            cls.WEIGHTS["session"]

        ) / 100

        reasons.append(session.reason)

        # ----------------------------------------------
        # Expiry
        # ----------------------------------------------

        score += (

            expiry.expiry_score

            *

            cls.WEIGHTS["expiry"]

        ) / 100

        reasons.append(expiry.reason)

        # ----------------------------------------------
        # Clamp
        # ----------------------------------------------

        score = max(0, min(score, 100))

        # ----------------------------------------------
        # Bias
        # ----------------------------------------------

        bias = trend.bias

        # ----------------------------------------------
        # Strategy
        # ----------------------------------------------

        strategy = cls._strategy(

            trend,

            volatility,

            liquidity,

        )

        # ----------------------------------------------
        # Warnings
        # ----------------------------------------------

        if liquidity.level.name == "LOW":

            warnings.append(

                "Low liquidity."

            )

        if volatility.level.name == "EXTREME":

            warnings.append(

                "Extreme volatility."

            )

        return FusionResult(

            market_score=round(score, 2),

            # confidence=round(confidence, 2),

            bias=bias,

            strategy=strategy,

            reasons=reasons,

            warnings=warnings,

        )

    # -----------------------------------------------------

    @staticmethod
    def _strategy(

        trend,

        volatility,

        liquidity,

    ):

        if liquidity.level.name == "LOW":

            return RecommendedStrategy.NO_TRADE

        if trend.trend.name in (

            "UPTREND",

            "STRONG_UPTREND",

        ):

            if volatility.level.name == "HIGH":

                return RecommendedStrategy.BREAKOUT

            return RecommendedStrategy.TREND_FOLLOWING

        if trend.trend.name in (

            "DOWNTREND",

            "STRONG_DOWNTREND",

        ):

            return RecommendedStrategy.TREND_FOLLOWING

        if trend.trend.name == "SIDEWAYS":

            return RecommendedStrategy.RANGE_TRADING

        return RecommendedStrategy.NO_TRADE