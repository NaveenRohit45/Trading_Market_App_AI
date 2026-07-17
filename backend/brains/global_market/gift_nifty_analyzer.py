"""
============================================================
Gift Nifty Analyzer
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Analyzes GIFT Nifty movement and estimates the
expected opening sentiment for the Indian market.

This analyzer only evaluates GIFT Nifty.

It does NOT consider:

- Live Market
- Options
- News
- Price Action

Those are handled by other AI brains.
"""

from __future__ import annotations

from .models import (
    GiftNiftyAnalysis,
    GiftNiftyTrend,
)


class GiftNiftyAnalyzer:

    @staticmethod
    def analyze(
        previous_close: float,
        current_price: float,
    ) -> GiftNiftyAnalysis:

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if previous_close <= 0:

            raise ValueError(
                "previous_close must be greater than zero."
            )

        # --------------------------------------------------
        # Calculate Gap
        # --------------------------------------------------

        points = current_price - previous_close

        percent = (
            points / previous_close
        ) * 100

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if percent >= 0.60:

            trend = GiftNiftyTrend.GAP_UP

            score = 95

            reason = (
                "Strong bullish gap expected."
            )

        elif percent >= 0.20:

            trend = GiftNiftyTrend.GAP_UP

            score = 80

            reason = (
                "Moderate bullish opening expected."
            )

        elif percent <= -0.60:

            trend = GiftNiftyTrend.GAP_DOWN

            score = 95

            reason = (
                "Strong bearish gap expected."
            )

        elif percent <= -0.20:

            trend = GiftNiftyTrend.GAP_DOWN

            score = 80

            reason = (
                "Moderate bearish opening expected."
            )

        else:

            trend = GiftNiftyTrend.FLAT

            score = 50

            reason = (
                "Flat opening expected."
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return GiftNiftyAnalysis(

            trend=trend,

            points=round(
                points,
                2,
            ),

            percent=round(
                percent,
                2,
            ),

            score=score,

            reason=reason,

        )