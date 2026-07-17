"""
============================================================
Asian Market Analyzer
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Analyzes major Asian markets before the Indian
market opens.

Markets Included

- Nikkei 225 (Japan)
- Hang Seng (Hong Kong)
- Shanghai Composite (China)

Returns

AsianMarketAnalysis

This analyzer only evaluates Asian markets.
It does NOT combine with US Markets, GIFT Nifty,
VIX, Currency or Commodities.
"""

from __future__ import annotations

from .models import (
    AsianMarketAnalysis,
    AsianMarketSentiment,
)


class AsianMarketAnalyzer:

    @staticmethod
    def analyze(
        nikkei_change: float,
        hang_seng_change: float,
        shanghai_change: float,
    ) -> AsianMarketAnalysis:

        # --------------------------------------------------
        # Average Market Performance
        # --------------------------------------------------

        average = (
            nikkei_change
            + hang_seng_change
            + shanghai_change
        ) / 3

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if average >= 1.50:

            sentiment = (
                AsianMarketSentiment.STRONG_POSITIVE
            )

            score = 100

            reason = (
                "Asian markets are strongly bullish."
            )

        elif average >= 0.50:

            sentiment = (
                AsianMarketSentiment.POSITIVE
            )

            score = 80

            reason = (
                "Asian markets are trading positive."
            )

        elif average <= -1.50:

            sentiment = (
                AsianMarketSentiment.STRONG_NEGATIVE
            )

            score = 0

            reason = (
                "Asian markets are strongly bearish."
            )

        elif average <= -0.50:

            sentiment = (
                AsianMarketSentiment.NEGATIVE
            )

            score = 20

            reason = (
                "Asian markets are trading negative."
            )

        else:

            sentiment = (
                AsianMarketSentiment.MIXED
            )

            score = 50

            reason = (
                "Asian markets are showing mixed performance."
            )

        # --------------------------------------------------
        # Return Result
        # --------------------------------------------------

        return AsianMarketAnalysis(

            sentiment=sentiment,

            nikkei_change=round(
                nikkei_change,
                2,
            ),

            hang_seng_change=round(
                hang_seng_change,
                2,
            ),

            shanghai_change=round(
                shanghai_change,
                2,
            ),

            score=score,

            reason=reason,

        )