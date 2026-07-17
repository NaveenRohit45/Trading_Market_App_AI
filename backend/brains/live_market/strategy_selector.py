"""
============================================================
Trading Market AI
Strategy Selector
Author : Super Cat
============================================================

Determines the best trading strategy based on
overall market conditions.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import RecommendedStrategy


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class StrategyResult:

    strategy: RecommendedStrategy

    confidence_modifier: float

    reason: str


# ============================================================
# Strategy Selector
# ============================================================

class StrategySelector:

    @classmethod
    def select(

        cls,

        trend,

        volatility,

        liquidity,

        session,

        expiry,

    ) -> StrategyResult:

        # ---------------------------------------------------
        # Safety Rules
        # ---------------------------------------------------

        if liquidity.level.name == "LOW":

            return StrategyResult(

                strategy=RecommendedStrategy.NO_TRADE,

                confidence_modifier=-25,

                reason="Market liquidity is too low.",

            )

        if volatility.level.name == "EXTREME":

            return StrategyResult(

                strategy=RecommendedStrategy.NO_TRADE,

                confidence_modifier=-20,

                reason="Extreme market volatility.",

            )

        # ---------------------------------------------------
        # Expiry Day
        # ---------------------------------------------------

        if expiry.is_expiry_day:

            if volatility.level.name in (

                "HIGH",

                "NORMAL",

            ):

                return StrategyResult(

                    strategy=RecommendedStrategy.SCALPING,

                    confidence_modifier=10,

                    reason="Expiry day favors scalping.",

                )

        # ---------------------------------------------------
        # Strong Uptrend
        # ---------------------------------------------------

        if trend.trend.name == "STRONG_UPTREND":

            if volatility.level.name == "HIGH":

                return StrategyResult(

                    strategy=RecommendedStrategy.BREAKOUT,

                    confidence_modifier=15,

                    reason="Strong trend with high volatility.",

                )

            return StrategyResult(

                strategy=RecommendedStrategy.TREND_FOLLOWING,

                confidence_modifier=10,

                reason="Strong bullish trend.",

            )

        # ---------------------------------------------------
        # Uptrend
        # ---------------------------------------------------

        if trend.trend.name == "UPTREND":

            return StrategyResult(

                strategy=RecommendedStrategy.TREND_FOLLOWING,

                confidence_modifier=8,

                reason="Bullish market structure.",

            )

        # ---------------------------------------------------
        # Downtrend
        # ---------------------------------------------------

        if trend.trend.name in (

            "DOWNTREND",

            "STRONG_DOWNTREND",

        ):

            return StrategyResult(

                strategy=RecommendedStrategy.TREND_FOLLOWING,

                confidence_modifier=8,

                reason="Bearish market structure.",

            )

        # ---------------------------------------------------
        # Sideways
        # ---------------------------------------------------

        if trend.trend.name == "SIDEWAYS":

            if session.session.name == "MIDDAY":

                return StrategyResult(

                    strategy=RecommendedStrategy.RANGE_TRADING,

                    confidence_modifier=5,

                    reason="Midday range-bound market.",

                )

            return StrategyResult(

                strategy=RecommendedStrategy.MEAN_REVERSION,

                confidence_modifier=4,

                reason="Sideways market.",

            )

        # ---------------------------------------------------
        # Reversal
        # ---------------------------------------------------

        if trend.trend.name in (

            "REVERSAL_UP",

            "REVERSAL_DOWN",

        ):

            return StrategyResult(

                strategy=RecommendedStrategy.REVERSAL,

                confidence_modifier=6,

                reason="Potential market reversal.",

            )

        # ---------------------------------------------------
        # Default
        # ---------------------------------------------------

        return StrategyResult(

            strategy=RecommendedStrategy.NO_TRADE,

            confidence_modifier=0,

            reason="No clear strategy available.",

        )