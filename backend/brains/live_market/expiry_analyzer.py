"""
============================================================
Live Market Brain
Expiry Analyzer
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .models import ExpiryType


# ============================================================
# Result Model
# ============================================================

@dataclass(slots=True)
class ExpiryAnalysis:
    """
    Result produced by Expiry Analyzer.
    """

    expiry_type: ExpiryType

    days_to_weekly: int
    days_to_monthly: int

    is_expiry_day: bool

    expiry_score: float

    reason: str


# ============================================================
# Analyzer
# ============================================================

class ExpiryAnalyzer:
    """
    Determines the market expiry status.

    Inputs
    ------
    today
    next_weekly_expiry
    next_monthly_expiry
    """

    @classmethod
    def analyze(
        cls,
        today: date,
        next_weekly_expiry: date,
        next_monthly_expiry: date,
    ) -> ExpiryAnalysis:

        days_to_weekly = (
            next_weekly_expiry - today
        ).days

        days_to_monthly = (
            next_monthly_expiry - today
        ).days

        # ----------------------------------------------------
        # Determine Expiry Type
        # ----------------------------------------------------

        if days_to_monthly == 0:

            expiry_type = ExpiryType.MONTHLY_EXPIRY

            score = 100

            reason = (
                "Today is Monthly Expiry."
            )

        elif days_to_weekly == 0:

            expiry_type = ExpiryType.WEEKLY_EXPIRY

            score = 80

            reason = (
                "Today is Weekly Expiry."
            )

        else:

            expiry_type = ExpiryType.NORMAL

            score = max(
                0,
                100 - (days_to_weekly * 10)
            )

            reason = (
                "Normal trading day."
            )

        return ExpiryAnalysis(

            expiry_type=expiry_type,

            days_to_weekly=days_to_weekly,

            days_to_monthly=days_to_monthly,

            is_expiry_day=(
                expiry_type
                != ExpiryType.NORMAL
            ),

            expiry_score=round(score, 2),

            reason=reason,
        )

    @classmethod
    def unavailable(cls):

        return ExpiryAnalysis(

            expiry_type=ExpiryType.NORMAL,

            days_to_weekly=0,

            days_to_monthly=0,

            is_expiry_day=False,

            expiry_score=50,

            reason="Expiry data unavailable.",

        )