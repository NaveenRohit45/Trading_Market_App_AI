"""
Market Regime Analyzer

Author : Super Cat
Project : Trading Market AI

Converts raw PredictionRecord into normalized
MarketFeatures for every AI brain.
"""

from __future__ import annotations

from datetime import datetime

from .models import (
    PredictionRecord,
    MarketFeatures,
)


class MarketRegimeAnalyzer:
    """
    Converts live market data into
    normalized market features.
    """

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def extract(
        self,
        prediction: PredictionRecord,
    ) -> MarketFeatures:

        atr_bucket = self._atr_bucket(
            prediction.atr
        )

        vix_bucket = self._vix_bucket(
            prediction.vix
        )

        market_session = self._market_session()

        confidence_bucket = self._confidence_bucket(
            prediction.confidence
        )

        brain_agreement = self._brain_agreement(
            prediction
        )

        support_distance = round(
            prediction.current_price - prediction.support,
            2,
        )

        resistance_distance = round(
            prediction.resistance - prediction.current_price,
            2,
        )

        return MarketFeatures(

            symbol=prediction.symbol,

            timeframe=prediction.timeframe,

            decision=prediction.decision,

            confidence=prediction.confidence,

            price_action=prediction.price_action_signal,

            live_market=prediction.live_market_signal,

            options=prediction.options_signal,

            global_market=prediction.global_market_signal,

            trend=prediction.trend,

            atr_bucket=atr_bucket,

            vix_bucket=vix_bucket,

            support_distance=support_distance,

            resistance_distance=resistance_distance,

            market_session=market_session,

            confidence_bucket=confidence_bucket,

            brain_agreement=brain_agreement,

            extra=prediction.extra.copy(),

        )

    # --------------------------------------------------
    # ATR Bucket
    # --------------------------------------------------

    @staticmethod
    def _atr_bucket(
        atr: float,
    ) -> str:

        if atr < 20:
            return "VERY_LOW"

        if atr < 40:
            return "LOW"

        if atr < 60:
            return "MEDIUM"

        if atr < 100:
            return "HIGH"

        return "VERY_HIGH"

    # --------------------------------------------------
    # VIX Bucket
    # --------------------------------------------------

    @staticmethod
    def _vix_bucket(
        vix: float,
    ) -> str:

        if vix < 12:
            return "VERY_LOW"

        if vix < 15:
            return "LOW"

        if vix < 18:
            return "MEDIUM"

        if vix < 22:
            return "HIGH"

        return "VERY_HIGH"

    # --------------------------------------------------
    # Confidence Bucket
    # --------------------------------------------------

    @staticmethod
    def _confidence_bucket(
        confidence: float,
    ) -> str:

        if confidence < 40:
            return "VERY_LOW"

        if confidence < 60:
            return "LOW"

        if confidence < 75:
            return "MEDIUM"

        if confidence < 90:
            return "HIGH"

        return "VERY_HIGH"

    # --------------------------------------------------
    # Market Session
    # --------------------------------------------------

    @staticmethod
    def _market_session() -> str:

        now = datetime.now()

        minutes = now.hour * 60 + now.minute

        if minutes < 555:
            return "PRE_OPEN"

        if minutes < 615:
            return "OPEN"

        if minutes < 720:
            return "MORNING"

        if minutes < 840:
            return "MIDDAY"

        if minutes < 915:
            return "AFTERNOON"

        return "CLOSE"

    # --------------------------------------------------
    # Brain Agreement
    # --------------------------------------------------

    @staticmethod
    def _brain_agreement(
        prediction: PredictionRecord,
    ) -> int:

        signals = [

            prediction.price_action_signal,

            prediction.live_market_signal,

            prediction.options_signal,

            prediction.global_market_signal,

        ]

        return sum(

            signal == prediction.decision

            for signal in signals

        )

