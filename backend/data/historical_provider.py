"""
Historical Market Data Provider

Downloads historical 1-minute candles from Yahoo Finance.

Author : Super Cat
Project: Trading_Market_App_AI
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List

import yfinance as yf

from backend.models import Candle

logger = logging.getLogger(__name__)


class HistoricalProvider:
    """
    Downloads historical market data.

    Returned candles are always chronological
    (oldest -> newest).
    """

    SYMBOL_MAP = {
        "NIFTY": "^NSEI",
        "SENSEX": "^BSESN",
        "^NSEI": "^NSEI",
        "^BSESN": "^BSESN",
    }

    def __init__(self):
        logger.info("HistoricalProvider initialized")

    def get_candles(
        self,
        symbol: str,
        period: str = "5d",
        interval: str = "1m",
    ) -> List[Candle]:
        """
        Download historical candles.

        Parameters
        ----------
        symbol
            NIFTY / SENSEX / Yahoo symbol

        period
            1d,5d,7d,1mo,...

        interval
            1m (recommended)

        Returns
        -------
        List[Candle]
        """

        yahoo_symbol = self.SYMBOL_MAP.get(symbol.upper(), symbol)

        logger.info(
            "Downloading %s (%s) period=%s interval=%s",
            symbol,
            yahoo_symbol,
            period,
            interval,
        )

        try:
            ticker = yf.Ticker(yahoo_symbol)

            df = ticker.history(
                period=period,
                interval=interval,
                auto_adjust=False,
                actions=False,
            )

        except Exception:
            logger.exception("Yahoo download failed.")
            return []

        if df.empty:
            logger.warning("No historical data returned.")
            return []

        candles: List[Candle] = []

        for timestamp, row in df.iterrows():

            ts = timestamp.to_pydatetime().timestamp()

            candles.append(
                Candle(
                    symbol=symbol,
                    start_ts=ts,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row.get("Volume", 0.0)),
                )
            )

        logger.info(
            "Downloaded %d candles for %s",
            len(candles),
            symbol,
        )

        return candles

    def latest(
        self,
        symbol: str,
    ) -> Candle | None:
        """
        Return the latest 1-minute candle.
        """

        candles = self.get_candles(
            symbol=symbol,
            period="1d",
            interval="1m",
        )

        if not candles:
            return None

        return candles[-1]