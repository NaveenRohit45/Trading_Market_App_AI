"""
============================================================
Live Market Brain
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from datetime import date, datetime

from .models import (
    LiveMarketAnalysis,
    MarketBias,
    RecommendedStrategy,
)

from .session_analyzer import SessionAnalyzer
from .gap_analyzer import GapAnalyzer
from .volatility_analyzer import VolatilityAnalyzer
from .liquidity_analyzer import LiquidityAnalyzer
from .trend_analyzer import TrendAnalyzer
from .market_strength import MarketStrengthAnalyzer
from .expiry_analyzer import ExpiryAnalyzer


class LiveMarketBrain:

    @classmethod
    def analyze(
            cls,
            *,
            now: datetime,
            candles,

            yesterday_close: float | None = None,
            today_open: float | None = None,

            current_volume: float | None = None,
            average_volume: float | None = None,
            tick_rate: float | None = None,

            nifty_change: float | None = None,
            sensex_change: float | None = None,
            banknifty_change: float | None = None,
            advance_decline_ratio: float | None = None,

            today: date | None = None,
            weekly_expiry: date | None = None,
            monthly_expiry: date | None = None,
    ):

        # -----------------------------------------
        # Execute Analyzers
        # -----------------------------------------

        session = SessionAnalyzer.analyze(now)

        if yesterday_close is not None and today_open is not None:

            gap = GapAnalyzer.analyze(
                yesterday_close,
                today_open,
            )
        else:
            gap = GapAnalyzer.unavailable()

        volatility = VolatilityAnalyzer.analyze(
            candles
        )

        if (
                current_volume is not None
                and average_volume is not None
                and tick_rate is not None
        ):
            liquidity = LiquidityAnalyzer.analyze(
                current_volume,
                average_volume,
                tick_rate,
            )
        else:
            liquidity = LiquidityAnalyzer.unavailable()
        trend = TrendAnalyzer.analyze(
            candles
        )

        if (
                nifty_change is not None
                and sensex_change is not None
                and banknifty_change is not None
                and advance_decline_ratio is not None
        ):
            strength = MarketStrengthAnalyzer.analyze(
                nifty_change,
                sensex_change,
                banknifty_change,
                advance_decline_ratio,
            )
        else:
            strength = MarketStrengthAnalyzer.unavailable()

        if (
                today is not None
                and weekly_expiry is not None
                and monthly_expiry is not None
        ):
            expiry = ExpiryAnalyzer.analyze(
                today,
                weekly_expiry,
                monthly_expiry,
            )
        else:
            expiry = ExpiryAnalyzer.unavailable()
        # -----------------------------------------
        # Fusion Score
        # -----------------------------------------

        score = 50

        score += (trend.trend_score - 50) * 0.45

        score += (strength.score - 50) * 0.30

        score += (liquidity.liquidity_score - 50) * 0.10

        score += (expiry.expiry_score - 50) * 0.05

        score += (volatility.volatility_score - 50) * 0.10

        score = max(0, min(score, 100))

        # confidence = score

        # -----------------------------------------
        # Bias
        # -----------------------------------------

        bias = trend.bias

        # -----------------------------------------
        # Strategy
        # -----------------------------------------

        strategy = cls._strategy(

            trend,

            volatility,

            liquidity,

        )

        # -----------------------------------------
        # Final Object
        # -----------------------------------------

        return LiveMarketAnalysis(

            market_state=trend.trend.value,

            market_bias=bias,

            # confidence=round(confidence, 2),

            market_score=round(score, 2),

            session=session.session,

            trend=trend.trend,

            volatility=volatility.level,

            gap=gap.gap_type,

            liquidity=liquidity.level,

            market_strength=strength.strength,

            expiry_type=expiry.expiry_type,

            recommended_strategy=strategy,

            reasons=[

                session.reason,

                trend.reason,

                gap.reason,

                volatility.reason,

                liquidity.reason,

                strength.reason,

                expiry.reason,

            ],

            warnings=[],

            details={

                "session": session,

                "gap": gap,

                "trend": trend,

                "volatility": volatility,

                "liquidity": liquidity,

                "strength": strength,

                "expiry": expiry,

            },

        )

    # ----------------------------------------------------

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