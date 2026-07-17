"""
============================================================
US Market Analyzer
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Analyzes overnight US market performance.

Tracks:

- Dow Jones
- Nasdaq
- S&P 500

Returns:

USMarketAnalysis

This analyzer does NOT determine the final
global sentiment. That is handled by the
Global Market Brain.
"""

from __future__ import annotations

from .models import (
    USMarketAnalysis,
    USMarketSentiment,
)


class USMarketAnalyzer:

    @staticmethod
    def analyze(
        dow_change: float,
        nasdaq_change: float,
        sp500_change: float,
    ) -> USMarketAnalysis:

        # --------------------------------------------------
        # Average Change
        # --------------------------------------------------

        average = (
            dow_change
            + nasdaq_change
            + sp500_change
        ) / 3

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if average >= 1.50:

            sentiment = USMarketSentiment.STRONG_POSITIVE

            score = 100

            reason = (
                "US markets closed with strong bullish momentum."
            )

        elif average >= 0.50:

            sentiment = USMarketSentiment.POSITIVE

            score = 80

            reason = (
                "US markets closed positive."
            )

        elif average <= -1.50:

            sentiment = USMarketSentiment.STRONG_NEGATIVE

            score = 0

            reason = (
                "US markets closed with strong bearish momentum."
            )

        elif average <= -0.50:

            sentiment = USMarketSentiment.NEGATIVE

            score = 20

            reason = (
                "US markets closed negative."
            )

        else:

            sentiment = USMarketSentiment.MIXED

            score = 50

            reason = (
                "US markets closed mixed."
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return USMarketAnalysis(

            sentiment=sentiment,

            dow_change=round(
                dow_change,
                2,
            ),

            nasdaq_change=round(
                nasdaq_change,
                2,
            ),

            sp500_change=round(
                sp500_change,
                2,
            ),

            score=score,

            reason=reason,

        )