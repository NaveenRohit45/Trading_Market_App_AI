"""
============================================================
Global Sentiment Engine V2
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Fuses all Global Market analyzers into a single
Global Market opinion.

V2 Features

✔ Weighted Scoring
✔ Agreement Detection
✔ Conflict Detection
✔ Confidence Calculation
✔ Positive Factors
✔ Negative Factors
✔ Warnings
"""

from __future__ import annotations

from .models import (
    GlobalSentiment,
    GlobalMarketBias,

    GiftNiftyTrend,
    USMarketSentiment,
    AsianMarketSentiment,
    VIXLevel,
    CurrencyStrength,
    CommoditySentiment,
)


class GlobalSentimentEngine:

    # ------------------------------------------
    # Weights
    # ------------------------------------------

    GIFT_WEIGHT = 0.30
    US_WEIGHT = 0.25
    ASIA_WEIGHT = 0.15
    VIX_WEIGHT = 0.15
    CURRENCY_WEIGHT = 0.10
    COMMODITY_WEIGHT = 0.05

    @classmethod
    def analyze(
        cls,
        gift,
        us,
        asia,
        vix,
        currency,
        commodity,
    ):

        positive = []
        negative = []
        warnings = []

        # ------------------------------------------
        # Weighted Score
        # ------------------------------------------

        score = (

            gift.score * cls.GIFT_WEIGHT +

            us.score * cls.US_WEIGHT +

            asia.score * cls.ASIA_WEIGHT +

            vix.score * cls.VIX_WEIGHT +

            currency.score * cls.CURRENCY_WEIGHT +

            commodity.score * cls.COMMODITY_WEIGHT

        )

        # ------------------------------------------
        # Agreement Detection
        # ------------------------------------------

        bullish = 0
        bearish = 0

        # Gift

        if gift.trend == GiftNiftyTrend.GAP_UP:
            bullish += 1
            positive.append(gift.reason)

        elif gift.trend == GiftNiftyTrend.GAP_DOWN:
            bearish += 1
            negative.append(gift.reason)

        # US

        if us.sentiment in (
            USMarketSentiment.POSITIVE,
            USMarketSentiment.STRONG_POSITIVE,
        ):
            bullish += 1
            positive.append(us.reason)

        elif us.sentiment in (
            USMarketSentiment.NEGATIVE,
            USMarketSentiment.STRONG_NEGATIVE,
        ):
            bearish += 1
            negative.append(us.reason)

        # Asia

        if asia.sentiment in (
            AsianMarketSentiment.POSITIVE,
            AsianMarketSentiment.STRONG_POSITIVE,
        ):
            bullish += 1
            positive.append(asia.reason)

        elif asia.sentiment in (
            AsianMarketSentiment.NEGATIVE,
            AsianMarketSentiment.STRONG_NEGATIVE,
        ):
            bearish += 1
            negative.append(asia.reason)

        # Currency

        if currency.strength in (
            CurrencyStrength.STRONG_RUPEE,
            CurrencyStrength.RUPEE,
        ):
            bullish += 1
            positive.append(currency.reason)

        elif currency.strength in (
            CurrencyStrength.WEAK_RUPEE,
            CurrencyStrength.VERY_WEAK_RUPEE,
        ):
            bearish += 1
            negative.append(currency.reason)

        # Commodity

        if commodity.sentiment == CommoditySentiment.BULLISH:
            bullish += 1
            positive.append(commodity.reason)

        elif commodity.sentiment == CommoditySentiment.BEARISH:
            bearish += 1
            negative.append(commodity.reason)

        # VIX

        if vix.level == VIXLevel.LOW:
            bullish += 1
            positive.append(vix.reason)

        elif vix.level in (
            VIXLevel.HIGH,
            VIXLevel.PANIC,
        ):
            bearish += 1
            warnings.append(vix.reason)

        # ------------------------------------------
        # Agreement
        # ------------------------------------------

        agreement = (
            max(
                bullish,
                bearish,
            )
            / 6
        ) * 100

        # ------------------------------------------
        # Conflict Penalty
        # ------------------------------------------

        conflicts = min(
            bullish,
            bearish,
        )

        score -= conflicts * 4

        score = max(
            0,
            min(
                100,
                score,
            ),
        )

        # ------------------------------------------
        # Confidence
        # ------------------------------------------

        # ------------------------------------------
        # Confidence
        # ------------------------------------------

        confidence = (

                agreement * 0.70 +

                abs(score - 50) * 0.30

        )

        confidence = max(

            0,

            min(

                100,

                confidence,

            ),

        )

        # ------------------------------------------
        # Final Sentiment
        # ------------------------------------------

        # ------------------------------------------
        # Final Sentiment
        # ------------------------------------------

        if score >= 90:

            sentiment = GlobalSentiment.STRONG_BULLISH
            bias = GlobalMarketBias.STRONG_BULLISH

        elif score >= 70:

            sentiment = GlobalSentiment.BULLISH
            bias = GlobalMarketBias.BULLISH

        elif score >= 45:

            sentiment = GlobalSentiment.NEUTRAL
            bias = GlobalMarketBias.NEUTRAL

        elif score >= 20:

            sentiment = GlobalSentiment.BEARISH
            bias = GlobalMarketBias.BEARISH

        else:

            sentiment = GlobalSentiment.STRONG_BEARISH
            bias = GlobalMarketBias.STRONG_BEARISH

        return {

            "sentiment": sentiment,

            "bias": bias,

            "score": round(score, 2),

            "confidence": round(confidence, 2),

            "agreement": round(agreement, 2),

            "positive_factors": positive,

            "negative_factors": negative,

            "warnings": warnings,

        }