"""
Feature Extractor

Trading Market AI V2

Converts raw prediction data into normalized
market features used by the Learning Brain.
"""

from __future__ import annotations

from datetime import datetime

from .models import (
    PredictionRecord,
    MarketFeatures,
)


class FeatureExtractor:

    """
    Converts PredictionRecord
    into MarketFeatures.
    """

    # =====================================================
    # Main
    # =====================================================

    def extract(
        self,
        prediction: PredictionRecord,
    ) -> MarketFeatures:

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

            atr_bucket=self.atr_bucket(
                prediction.atr
            ),

            vix_bucket=self.vix_bucket(
                prediction.vix
            ),

            support_distance=round(
                prediction.current_price -
                prediction.support,
                2,
            ),

            resistance_distance=round(
                prediction.resistance -
                prediction.current_price,
                2,
            ),

            market_session=self.market_session(),

            confidence_bucket=self.confidence_bucket(
                prediction.confidence
            ),

            brain_agreement=self.brain_agreement(
                prediction
            ),

            extra=prediction.extra,
        )

    # =====================================================
    # ATR
    # =====================================================

    @staticmethod
    def atr_bucket(
        atr: float,
    ) -> str:

        if atr < 10:
            return "LOW"

        elif atr < 20:
            return "MEDIUM"

        elif atr < 35:
            return "HIGH"

        return "EXTREME"

    # =====================================================
    # VIX
    # =====================================================

    @staticmethod
    def vix_bucket(
        vix: float,
    ) -> str:

        if vix < 12:
            return "LOW"

        elif vix < 18:
            return "NORMAL"

        elif vix < 25:
            return "HIGH"

        return "EXTREME"

    # =====================================================
    # Session
    # =====================================================

    @staticmethod
    def market_session() -> str:

        now = datetime.now().time()

        if now.hour == 9 and now.minute < 45:
            return "OPEN"

        if now.hour < 12:
            return "MORNING"

        if now.hour < 14:
            return "MIDDAY"

        return "CLOSING"

    # =====================================================
    # Confidence
    # =====================================================

    @staticmethod
    def confidence_bucket(
        confidence: float,
    ) -> str:

        if confidence < 50:
            return "LOW"

        elif confidence < 70:
            return "MEDIUM"

        elif confidence < 85:
            return "HIGH"

        return "VERY_HIGH"

    # =====================================================
    # Brain Agreement
    # =====================================================

    @staticmethod
    def brain_agreement(
        prediction: PredictionRecord,
    ) -> int:

        signals = [

            prediction.price_action_signal,

            prediction.live_market_signal,

            prediction.options_signal,

            prediction.global_market_signal,

        ]

        decision = prediction.decision

        return sum(
            1
            for signal in signals
            if signal == decision
        )