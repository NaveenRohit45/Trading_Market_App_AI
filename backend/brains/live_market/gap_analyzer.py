"""
============================================================
Live Market Brain
Gap Analyzer
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import GapType


@dataclass(slots=True)
class GapAnalysis:
    """
    Result produced by Gap Analyzer.
    """

    gap_type: GapType
    gap_points: float
    gap_percent: float
    is_gap_significant: bool
    reason: str


class GapAnalyzer:
    """
    Determines today's opening gap.

    Formula
    -------
    Gap Points  = Today's Open - Yesterday Close

    Gap Percent = (Gap Points / Yesterday Close) * 100
    """

    # Gap percentage threshold
    SIGNIFICANT_GAP_PERCENT = 0.50

    @classmethod
    def analyze(
        cls,
        yesterday_close: float,
        today_open: float,
    ) -> GapAnalysis:

        if yesterday_close <= 0:
            raise ValueError("Yesterday close must be greater than zero.")

        gap_points = today_open - yesterday_close

        gap_percent = (
            gap_points / yesterday_close
        ) * 100

        if gap_points > 0:
            gap = GapType.GAP_UP
            reason = "Market opened above yesterday's close."

        elif gap_points < 0:
            gap = GapType.GAP_DOWN
            reason = "Market opened below yesterday's close."

        else:
            gap = GapType.FLAT
            reason = "Market opened exactly at yesterday's close."

        significant = (
            abs(gap_percent)
            >= cls.SIGNIFICANT_GAP_PERCENT
        )

        return GapAnalysis(
            gap_type=gap,
            gap_points=round(gap_points, 2),
            gap_percent=round(gap_percent, 2),
            is_gap_significant=significant,
            reason=reason,
        )

    @classmethod
    def unavailable(cls):

        return GapAnalysis(
            gap_type=GapType.FLAT,
            gap_points=0,
            gap_percent=0,
            is_gap_significant=False,
            reason="Gap data unavailable.",
        )