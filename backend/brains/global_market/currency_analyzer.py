"""
============================================================
Currency Analyzer
Trading Market AI
Author : Super Cat
============================================================

Purpose
-------
Analyzes USD/INR exchange rate.

A stronger Rupee is generally supportive for
Indian equities.

A weaker Rupee may indicate FII outflows,
higher import costs and increased volatility.

Returns

CurrencyAnalysis
"""

from __future__ import annotations

from .models import (
    CurrencyAnalysis,
    CurrencyStrength,
)


class CurrencyAnalyzer:

    @staticmethod
    def analyze(
        usd_inr: float,
    ) -> CurrencyAnalysis:

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if usd_inr <= 0:

            raise ValueError(
                "USD/INR must be greater than zero."
            )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if usd_inr < 82:

            strength = CurrencyStrength.STRONG_RUPEE

            score = 95

            reason = (
                "Strong Indian Rupee. Positive for equities."
            )

        elif usd_inr < 84:

            strength = CurrencyStrength.RUPEE

            score = 80

            reason = (
                "Healthy Rupee. Market friendly."
            )

        elif usd_inr < 86:

            strength = CurrencyStrength.NEUTRAL

            score = 60

            reason = (
                "Neutral currency movement."
            )

        elif usd_inr < 88:

            strength = CurrencyStrength.WEAK_RUPEE

            score = 35

            reason = (
                "Weak Rupee. Possible pressure on equities."
            )

        else:

            strength = CurrencyStrength.VERY_WEAK_RUPEE

            score = 10

            reason = (
                "Very weak Rupee. High currency risk."
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return CurrencyAnalysis(

            strength=strength,

            usd_inr=round(
                usd_inr,
                2,
            ),

            score=score,

            reason=reason,

        )