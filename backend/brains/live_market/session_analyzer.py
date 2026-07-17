"""
============================================================
Live Market Brain
Session Analyzer
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time

from .models import MarketSession


@dataclass(slots=True)
class SessionAnalysis:
    """
    Output of Session Analyzer.
    """

    session: MarketSession
    minutes_from_open: int
    minutes_to_close: int
    is_market_open: bool
    reason: str


class SessionAnalyzer:
    """
    Determines the current Indian stock market session.

    NSE Market Hours
    ----------------
    Pre Market  : 09:00 - 09:15
    Open        : 09:15 - 09:45
    Morning     : 09:45 - 11:30
    Midday      : 11:30 - 13:30
    Afternoon   : 13:30 - 15:00
    Closing     : 15:00 - 15:30
    Post Market : 15:30 - 16:00
    Closed      : Otherwise
    """

    PRE_MARKET_START = time(9, 0)
    MARKET_OPEN = time(9, 15)
    OPENING_END = time(9, 45)
    MORNING_END = time(11, 30)
    MIDDAY_END = time(13, 30)
    AFTERNOON_END = time(15, 0)
    MARKET_CLOSE = time(15, 30)
    POST_MARKET_END = time(16, 0)

    @classmethod
    def analyze(cls, now: datetime | None = None) -> SessionAnalysis:
        """
        Analyze current market session.

        Parameters
        ----------
        now : datetime, optional
            Used for unit testing.
            Defaults to current system time.

        Returns
        -------
        SessionAnalysis
        """

        now = now or datetime.now()

        current = now.time()

        open_dt = datetime.combine(now.date(), cls.MARKET_OPEN)
        close_dt = datetime.combine(now.date(), cls.MARKET_CLOSE)

        minutes_from_open = int((now - open_dt).total_seconds() / 60)
        minutes_to_close = int((close_dt - now).total_seconds() / 60)

        if cls.PRE_MARKET_START <= current < cls.MARKET_OPEN:
            return SessionAnalysis(
                session=MarketSession.PRE_MARKET,
                minutes_from_open=max(minutes_from_open, 0),
                minutes_to_close=max(minutes_to_close, 0),
                is_market_open=False,
                reason="Pre-market session",
            )

        if cls.MARKET_OPEN <= current < cls.OPENING_END:
            return SessionAnalysis(
                session=MarketSession.OPENING,
                minutes_from_open=max(minutes_from_open, 0),
                minutes_to_close=max(minutes_to_close, 0),
                is_market_open=True,
                reason="High volatility opening session",
            )

        if cls.OPENING_END <= current < cls.MORNING_END:
            return SessionAnalysis(
                session=MarketSession.MORNING,
                minutes_from_open=minutes_from_open,
                minutes_to_close=minutes_to_close,
                is_market_open=True,
                reason="Morning trend development",
            )

        if cls.MORNING_END <= current < cls.MIDDAY_END:
            return SessionAnalysis(
                session=MarketSession.MIDDAY,
                minutes_from_open=minutes_from_open,
                minutes_to_close=minutes_to_close,
                is_market_open=True,
                reason="Midday low volatility",
            )

        if cls.MIDDAY_END <= current < cls.AFTERNOON_END:
            return SessionAnalysis(
                session=MarketSession.AFTERNOON,
                minutes_from_open=minutes_from_open,
                minutes_to_close=minutes_to_close,
                is_market_open=True,
                reason="Afternoon trend continuation",
            )

        if cls.AFTERNOON_END <= current < cls.MARKET_CLOSE:
            return SessionAnalysis(
                session=MarketSession.CLOSING,
                minutes_from_open=minutes_from_open,
                minutes_to_close=max(minutes_to_close, 0),
                is_market_open=True,
                reason="Closing hour with institutional activity",
            )

        if cls.MARKET_CLOSE <= current < cls.POST_MARKET_END:
            return SessionAnalysis(
                session=MarketSession.POST_MARKET,
                minutes_from_open=minutes_from_open,
                minutes_to_close=0,
                is_market_open=False,
                reason="Post-market session",
            )

        return SessionAnalysis(
            session=MarketSession.CLOSED,
            minutes_from_open=0,
            minutes_to_close=0,
            is_market_open=False,
            reason="Market closed",
        )