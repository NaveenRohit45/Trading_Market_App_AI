"""
============================================================
Global Market Brain
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Main orchestrator for the Global Market Brain.

Runs:

• Gift Nifty Analyzer
• US Market Analyzer
• Asian Market Analyzer
• VIX Analyzer
• Currency Analyzer
• Commodity Analyzer

Then combines everything using the
GlobalSentimentEngine.

Returns

GlobalMarketAnalysis
"""

from __future__ import annotations

from .models import (
    GlobalMarketAnalysis,
)

from .gift_nifty_analyzer import (
    GiftNiftyAnalyzer,
)

from .us_market_analyzer import (
    USMarketAnalyzer,
)

from .asian_market_analyzer import (
    AsianMarketAnalyzer,
)

from .vix_analyzer import (
    VIXAnalyzer,
)

from .currency_analyzer import (
    CurrencyAnalyzer,
)

from .commodity_analyzer import (
    CommodityAnalyzer,
)

from .global_sentiment import (
    GlobalSentimentEngine,
)


class GlobalMarketBrain:

    @classmethod
    def analyze(
        cls,

        # ------------------------------
        # Gift Nifty
        # ------------------------------

        gift_previous_close: float,
        gift_current_price: float,

        # ------------------------------
        # US Markets
        # ------------------------------

        dow_change: float,
        nasdaq_change: float,
        sp500_change: float,

        # ------------------------------
        # Asian Markets
        # ------------------------------

        nikkei_change: float,
        hang_seng_change: float,
        shanghai_change: float,

        # ------------------------------
        # India VIX
        # ------------------------------

        india_vix: float,

        # ------------------------------
        # Currency
        # ------------------------------

        usd_inr: float,

        # ------------------------------
        # Commodities
        # ------------------------------

        gold_change: float,
        crude_change: float,

    ) -> GlobalMarketAnalysis:

        # ==================================================
        # Execute Individual Analyzers
        # ==================================================

        gift = GiftNiftyAnalyzer.analyze(
            gift_previous_close,
            gift_current_price,
        )

        us = USMarketAnalyzer.analyze(
            dow_change,
            nasdaq_change,
            sp500_change,
        )

        asia = AsianMarketAnalyzer.analyze(
            nikkei_change,
            hang_seng_change,
            shanghai_change,
        )

        vix = VIXAnalyzer.analyze(
            india_vix,
        )

        currency = CurrencyAnalyzer.analyze(
            usd_inr,
        )

        commodity = CommodityAnalyzer.analyze(
            gold_change,
            crude_change,
        )

        # ==================================================
        # Global Sentiment
        # ==================================================

        sentiment = GlobalSentimentEngine.analyze(

            gift=gift,

            us=us,

            asia=asia,

            vix=vix,

            currency=currency,

            commodity=commodity,

        )

        # ==================================================
        # Build Final Analysis
        # ==================================================

        return GlobalMarketAnalysis(

            overall_sentiment=sentiment["sentiment"],

            market_bias=sentiment["bias"],

            market_score=sentiment["score"],

            us_market=us.sentiment,

            asian_market=asia.sentiment,

            gift_nifty=gift.trend,

            vix=vix.level,

            currency=currency.strength,

            commodity=commodity.sentiment,

            confidence=sentiment["confidence"],

            agreement=sentiment["agreement"],

            positive_factors=sentiment["positive_factors"],

            negative_factors=sentiment["negative_factors"],

            reasons=(
                    sentiment["positive_factors"]
                    + sentiment["negative_factors"]
            ),

            warnings=sentiment["warnings"],



            details={

                "gift_nifty": gift,

                "us_market": us,

                "asian_market": asia,

                "vix": vix,

                "currency": currency,

                "commodity": commodity,

            },

        )