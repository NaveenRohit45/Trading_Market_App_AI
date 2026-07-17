"""
Trading Market AI V2

Fingerprint Generator

Converts MarketFeatures into a deterministic
market fingerprint.

Author : Super Cat
"""

from __future__ import annotations

import hashlib
import json

from .models import MarketFeatures


class FingerprintGenerator:
    """
    Generates unique fingerprints for market setups.
    """

    def __init__(self):

        self.version = "2.0"

    # =====================================================
    # Public API
    # =====================================================

    def generate(
        self,
        features: MarketFeatures,
    ) -> str:
        """
        Generate SHA256 fingerprint.
        """

        payload = self.to_dictionary(features)

        normalized = json.dumps(

            payload,

            sort_keys=True,

            separators=(",", ":")

        )

        return hashlib.sha256(

            normalized.encode("utf-8")

        ).hexdigest()

    # =====================================================
    # Dictionary
    # =====================================================

    def to_dictionary(
        self,
        features: MarketFeatures,
    ) -> dict:

        return {

            "version": self.version,

            "symbol": features.symbol,

            "timeframe": features.timeframe,

            "decision": features.decision,

            "price_action": features.price_action,

            "live_market": features.live_market,

            "options": features.options,

            "global_market": features.global_market,

            "trend": features.trend,

            "atr": features.atr_bucket,

            "vix": features.vix_bucket,

            "support_distance":
                self.distance_bucket(
                    features.support_distance
                ),

            "resistance_distance":
                self.distance_bucket(
                    features.resistance_distance
                ),

            "market_session":
                features.market_session,

            "confidence":
                features.confidence_bucket,

            "brain_agreement":
                features.brain_agreement,

        }

    # =====================================================
    # Distance Bucket
    # =====================================================

    @staticmethod
    def distance_bucket(
        distance: float,
    ) -> str:

        distance = abs(distance)

        if distance < 10:
            return "VERY_NEAR"

        elif distance < 25:
            return "NEAR"

        elif distance < 50:
            return "MEDIUM"

        return "FAR"

    # =====================================================
    # Human Readable
    # =====================================================

    def readable(
        self,
        features: MarketFeatures,
    ) -> str:

        payload = self.to_dictionary(features)

        return " | ".join(

            f"{k}:{v}"

            for k, v in payload.items()

        )

    # =====================================================
    # Verify
    # =====================================================

    def verify(
        self,
        features: MarketFeatures,
        fingerprint: str,
    ) -> bool:

        return self.generate(features) == fingerprint

    # =====================================================
    # Compare
    # =====================================================

    def same_pattern(
        self,
        left: MarketFeatures,
        right: MarketFeatures,
    ) -> bool:

        return (

            self.generate(left)

            ==

            self.generate(right)

        )