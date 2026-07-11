"""
premium_flow.py

Premium Flow Analyzer

Responsible for:
- Premium Momentum
- Volume Momentum
- Smart Money Detection
- Bullish/Bearish Premium Flow
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


@dataclass
class PremiumFlowAnalysis:

    signal: str

    confidence: int

    dominant_side: str

    reasons: List[str]

    details: Dict


class PremiumFlowAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> PremiumFlowAnalysis:

        total_call_premium = 0.0
        total_put_premium = 0.0

        total_call_volume = 0
        total_put_volume = 0

        reasons = []

        confidence = 50

        # ---------------------------------------

        for option in chain.options:

            total_call_premium += (
                option.call_ltp * option.call_volume
            )

            total_put_premium += (
                option.put_ltp * option.put_volume
            )

            total_call_volume += option.call_volume
            total_put_volume += option.put_volume

        # ---------------------------------------

        if total_call_premium > total_put_premium:

            signal = "Bullish"

            dominant = "CALL"

            confidence += 20

            reasons.append(
                "Call premium flow dominates."
            )

        elif total_put_premium > total_call_premium:

            signal = "Bearish"

            dominant = "PUT"

            confidence += 20

            reasons.append(
                "Put premium flow dominates."
            )

        else:

            signal = "Neutral"

            dominant = "NONE"

        # ---------------------------------------
        # Volume Confirmation
        # ---------------------------------------

        if total_call_volume > total_put_volume:

            reasons.append(
                "Call volume higher than Put volume."
            )

            if dominant == "CALL":
                confidence += 10

        elif total_put_volume > total_call_volume:

            reasons.append(
                "Put volume higher than Call volume."
            )

            if dominant == "PUT":
                confidence += 10

        # ---------------------------------------
        # Smart Money Heuristic
        # ---------------------------------------

        smart_money = "Unknown"

        if (
            total_call_premium > total_put_premium
            and total_call_volume > total_put_volume
        ):

            smart_money = "CALL BUYERS"

            confidence += 10

            reasons.append(
                "Premium and volume confirm Call buying."
            )

        elif (
            total_put_premium > total_call_premium
            and total_put_volume > total_call_volume
        ):

            smart_money = "PUT BUYERS"

            confidence += 10

            reasons.append(
                "Premium and volume confirm Put buying."
            )

        confidence = min(confidence, 100)

        # ---------------------------------------

        return PremiumFlowAnalysis(

            signal=signal,

            confidence=confidence,

            dominant_side=dominant,

            reasons=reasons,

            details={

                "call_premium": round(total_call_premium, 2),

                "put_premium": round(total_put_premium, 2),

                "call_volume": total_call_volume,

                "put_volume": total_put_volume,

                "smart_money": smart_money

            }

        )