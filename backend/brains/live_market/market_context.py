"""
============================================================
Trading Market AI
Market Context Engine
Author : Super Cat
============================================================

Determines the overall market environment.

This module combines outputs from all analyzers and
returns the current market context.

Example

TRENDING

RANGING

BREAKOUT

REVERSAL

LOW_VOLUME

HIGH_VOLATILITY

EXPIRY

NO_TRADE
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ============================================================
# Market Context
# ============================================================

class MarketContext(str, Enum):

    TRENDING = "TRENDING"

    STRONG_TREND = "STRONG_TREND"

    BREAKOUT = "BREAKOUT"

    REVERSAL = "REVERSAL"

    RANGING = "RANGING"

    HIGH_VOLATILITY = "HIGH_VOLATILITY"

    LOW_LIQUIDITY = "LOW_LIQUIDITY"

    EXPIRY = "EXPIRY"

    NO_TRADE = "NO_TRADE"


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class MarketContextResult:

    context: MarketContext

    score: float

    reason: str


# ============================================================
# Engine
# ============================================================

class MarketContextEngine:

    @classmethod
    def determine(

        cls,

        trend,

        volatility,

        liquidity,

        strength,

        session,

        expiry,

    ) -> MarketContextResult:

        # --------------------------------------------------
        # Safety First
        # --------------------------------------------------

        if liquidity.level.name == "LOW":

            return MarketContextResult(

                context=MarketContext.LOW_LIQUIDITY,

                score=20,

                reason="Market participation is too low.",

            )

        if volatility.level.name == "EXTREME":

            return MarketContextResult(

                context=MarketContext.HIGH_VOLATILITY,

                score=35,

                reason="Extreme volatility detected.",

            )

        # --------------------------------------------------
        # Expiry
        # --------------------------------------------------

        if expiry.is_expiry_day:

            return MarketContextResult(

                context=MarketContext.EXPIRY,

                score=70,

                reason="Expiry day market.",

            )

        # --------------------------------------------------
        # Strong Trend
        # --------------------------------------------------

        if (

            trend.trend.name == "STRONG_UPTREND"

            and

            strength.score > 80

        ):

            return MarketContextResult(

                context=MarketContext.STRONG_TREND,

                score=95,

                reason="Strong bullish market.",

            )

        if (

            trend.trend.name == "STRONG_DOWNTREND"

            and

            strength.score < 30

        ):

            return MarketContextResult(

                context=MarketContext.STRONG_TREND,

                score=95,

                reason="Strong bearish market.",

            )

        # --------------------------------------------------
        # Trend
        # --------------------------------------------------

        if trend.trend.name in (

            "UPTREND",

            "DOWNTREND",

        ):

            return MarketContextResult(

                context=MarketContext.TRENDING,

                score=82,

                reason="Trending market.",

            )

        # --------------------------------------------------
        # Breakout
        # --------------------------------------------------

        if (

            volatility.level.name == "HIGH"

            and

            liquidity.level.name == "HIGH"

            and

            session.session.name == "OPENING"

        ):

            return MarketContextResult(

                context=MarketContext.BREAKOUT,

                score=90,

                reason="Breakout conditions detected.",

            )

        # --------------------------------------------------
        # Reversal
        # --------------------------------------------------

        if trend.trend.name in (

            "REVERSAL_UP",

            "REVERSAL_DOWN",

        ):

            return MarketContextResult(

                context=MarketContext.REVERSAL,

                score=80,

                reason="Potential market reversal.",

            )

        # --------------------------------------------------
        # Sideways
        # --------------------------------------------------

        return MarketContextResult(

            context=MarketContext.RANGING,

            score=55,

            reason="Range-bound market.",

        )