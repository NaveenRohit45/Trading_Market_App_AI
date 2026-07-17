"""
Historical Loader

Loads historical candles into the Candle Engine before
the live market feed starts.

Author : Super Cat
Project: Trading_Market_App_AI
"""

from __future__ import annotations

import logging

from backend.core.candle_aggregator import CandleAggregator
from backend.core.candle_engine import CandleEngine
from backend.data.historical_provider import HistoricalProvider

logger = logging.getLogger(__name__)


class HistoricalLoader:
    """
    Preloads historical candles into the Candle Engine.
    """

    def __init__(
        self,
        engine: CandleEngine,
        groww_provider=None,
    ):
        self.engine = engine
        self.provider = HistoricalProvider()
        # If a live, authenticated GrowwProvider is passed in, prefer it
        # over Yahoo Finance for historical candles (more reliable,
        # same data source as the live feed).
        self.groww_provider = groww_provider

    def load(
        self,
        symbol: str,
        interval: int = 180,
        period: str = "5d",
    ) -> bool:
        """
        Load historical candles.

        Parameters
        ----------
        symbol
            NIFTY / SENSEX

        interval
            Target candle interval in seconds.
            Default = 180 (3 minutes)

        period
            Yahoo download period.

        Returns
        -------
        bool
            True if history loaded.
        """

        logger.info("--------------------------------------------")
        logger.info("Loading history for %s", symbol)

        history_1m = self.provider.get_candles(
            symbol=symbol,
            period=period,
            interval="1m",
        )

        if not history_1m:
            logger.warning("No historical data found.")
            return False

        timeframe_minutes = interval // 60

        history = CandleAggregator.aggregate(
            history_1m,
            timeframe_minutes=timeframe_minutes,
        )

        self.engine.load_history(
            symbol=symbol,
            interval=interval,
            candles=history,
        )

        logger.info(
            "Loaded %d historical %dm candles for %s",
            len(history),
            timeframe_minutes,
            symbol,
        )

        return True

    def load_all_timeframes(
            self,
            symbol: str,
            period: str = "5d",
    ):
        """
        Download history once and build all required timeframes.
        """

        logger.info("=" * 60)
        logger.info("Loading all timeframes for %s", symbol)

        # --------------------------------------------------
        # PREFER GROWW (same source as live feed, reliable).
        # FALL BACK TO YAHOO FINANCE ONLY IF GROWW UNAVAILABLE.
        # --------------------------------------------------

        history_1m = []

        if self.groww_provider is not None:
            try:
                history_1m = self.groww_provider.get_historical_candles(
                    symbol=symbol,
                    interval_minutes=1,
                    days_back=int(period.rstrip("d")) if period.endswith("d") else 5,
                )
            except Exception as error:
                logger.warning("Groww historical fetch failed for %s: %s", symbol, error)
                history_1m = []

        if not history_1m:
            logger.warning("Falling back to Yahoo Finance for %s historical data.", symbol)
            history_1m = self.provider.get_candles(
                symbol=symbol,
                period=period,
                interval="1m",
            )

        if not history_1m:
            logger.warning("No historical data found from any source.")
            return None

        # --------------------------
        # 1 Minute
        # --------------------------

        self.engine.load_history(
            symbol=symbol,
            interval=60,
            candles=history_1m,
        )

        # --------------------------
        # 2 Minute
        # --------------------------

        history_2m = CandleAggregator.aggregate(
            history_1m,
            timeframe_minutes=2,
        )

        self.engine.load_history(
            symbol=symbol,
            interval=120,
            candles=history_2m,
        )

        # --------------------------
        # 3 Minute
        # --------------------------

        history_3m = CandleAggregator.aggregate(
            history_1m,
            timeframe_minutes=3,
        )

        self.engine.load_history(
            symbol=symbol,
            interval=180,
            candles=history_3m,
        )

        # --------------------------
        # 5 Minute
        # --------------------------

        history_5m = CandleAggregator.aggregate(
            history_1m,
            timeframe_minutes=5,
        )

        self.engine.load_history(
            symbol=symbol,
            interval=300,
            candles=history_5m,
        )

        logger.info(
            "%s loaded | 1m=%d 2m=%d 3m=%d 5m=%d",
            symbol,
            len(history_1m),
            len(history_2m),
            len(history_3m),
            len(history_5m),
        )

        return {
            "1m": len(history_1m),
            "2m": len(history_2m),
            "3m": len(history_3m),
            "5m": len(history_5m),
        }

    def load_multiple(
            self,
            symbols: list[str],
            period: str = "5d",
    ):
        """
        Load all symbols and all timeframes.
        """

        results = {}

        for symbol in symbols:
            results[symbol] = self.load_all_timeframes(
                symbol=symbol,
                period=period,
            )

        return results