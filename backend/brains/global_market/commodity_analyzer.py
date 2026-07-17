"""
============================================================
Commodity Analyzer
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Analyzes important global commodities.

Tracks:

- Gold
- Crude Oil

Returns

CommodityAnalysis

This analyzer ONLY evaluates commodities.

It does NOT combine with:

- US Market
- Asian Market
- GIFT Nifty
- Currency
- India VIX

That is handled by GlobalMarketBrain.
"""

from __future__ import annotations

from .models import (
    CommodityAnalysis,
    CommoditySentiment,
)


class CommodityAnalyzer:

    @staticmethod
    def analyze(
        gold_change: float,
        crude_change: float,
    ) -> CommodityAnalysis:

        # --------------------------------------------------
        # Gold Analysis
        #
        # Rising Gold:
        # Safe-haven buying
        # Slightly bearish for equities
        #
        # Falling Gold:
        # Risk-on sentiment
        # Bullish for equities
        # --------------------------------------------------

        if gold_change >= 1.5:

            gold_score = -25

            gold_reason = (
                "Gold rising sharply indicates risk-off sentiment."
            )

        elif gold_change >= 0.5:

            gold_score = -10

            gold_reason = (
                "Gold gaining moderately."
            )

        elif gold_change <= -1.5:

            gold_score = 25

            gold_reason = (
                "Gold falling sharply supports equities."
            )

        elif gold_change <= -0.5:

            gold_score = 10

            gold_reason = (
                "Gold weakening slightly."
            )

        else:

            gold_score = 0

            gold_reason = (
                "Gold is stable."
            )

        # --------------------------------------------------
        # Crude Oil Analysis
        #
        # India imports crude.
        # Higher crude prices usually pressure equities.
        # --------------------------------------------------

        if crude_change >= 2.0:

            crude_score = -35

            crude_reason = (
                "Crude oil rising sharply."
            )

        elif crude_change >= 1.0:

            crude_score = -20

            crude_reason = (
                "Crude oil gaining."
            )

        elif crude_change <= -2.0:

            crude_score = 35

            crude_reason = (
                "Crude oil falling sharply."
            )

        elif crude_change <= -1.0:

            crude_score = 20

            crude_reason = (
                "Crude oil easing."
            )

        else:

            crude_score = 0

            crude_reason = (
                "Crude oil stable."
            )

        # --------------------------------------------------
        # Final Commodity Score
        # --------------------------------------------------

        raw_score = gold_score + crude_score

        score = max(
            0,
            min(
                100,
                50 + raw_score,
            ),
        )

        # --------------------------------------------------
        # Sentiment
        # --------------------------------------------------

        if score >= 80:

            sentiment = CommoditySentiment.BULLISH

            summary = (
                "Commodity environment supports equities."
            )

        elif score <= 20:

            sentiment = CommoditySentiment.BEARISH

            summary = (
                "Commodity environment is unfavorable for equities."
            )

        else:

            sentiment = CommoditySentiment.NEUTRAL

            summary = (
                "Commodity impact is neutral."
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return CommodityAnalysis(

            sentiment=sentiment,

            gold_change=round(
                gold_change,
                2,
            ),

            crude_change=round(
                crude_change,
                2,
            ),

            score=round(
                score,
                2,
            ),

            reason=(
                summary
                + " "
                + gold_reason
                + " "
                + crude_reason
            ),

        )