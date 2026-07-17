"""
Candle Aggregator

Converts lower timeframe candles into higher timeframe candles.

Example:
    1 Minute -> 3 Minute
    1 Minute -> 5 Minute
    1 Minute -> 15 Minute

Author : Super Cat
Project: Trading_Market_App_AI
"""

from __future__ import annotations

from typing import List

from backend.models import Candle


class CandleAggregator:
    """
    Aggregates candles into larger timeframe candles.
    """

    @staticmethod
    def aggregate(
        candles: List[Candle],
        timeframe_minutes: int,
    ) -> List[Candle]:
        """
        Aggregate candles.

        Parameters
        ----------
        candles
            Input candles sorted oldest -> newest.

        timeframe_minutes
            Output timeframe.

        Returns
        -------
        List[Candle]
        """

        if timeframe_minutes <= 1:
            return candles.copy()

        if not candles:
            return []

        aggregated: List[Candle] = []

        bucket: List[Candle] = []

        timeframe_seconds = timeframe_minutes * 60

        current_bucket = int(candles[0].start_ts // timeframe_seconds)

        for candle in candles:

            bucket_id = int(candle.start_ts // timeframe_seconds)

            if bucket_id != current_bucket:

                aggregated.append(
                    CandleAggregator._merge(bucket)
                )

                bucket = []

                current_bucket = bucket_id

            bucket.append(candle)

        if bucket:
            aggregated.append(
                CandleAggregator._merge(bucket)
            )

        return aggregated

    @staticmethod
    def _merge(
        candles: List[Candle],
    ) -> Candle:

        first = candles[0]
        last = candles[-1]

        return Candle(
            symbol=first.symbol,
            start_ts=first.start_ts,
            open=first.open,
            high=max(c.high for c in candles),
            low=min(c.low for c in candles),
            close=last.close,
            volume=sum(c.volume for c in candles),
        )