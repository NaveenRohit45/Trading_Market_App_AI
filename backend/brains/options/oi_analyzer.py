"""
oi_analyzer.py

Open Interest Analyzer

Responsible for

• Support
• Resistance
• Call Writing
• Put Writing
• Long Build-up
• Short Build-up
• Long Unwinding
• Short Covering
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


@dataclass
class OIAnalysis:

    signal: str

    confidence: int

    support: float

    resistance: float

    reasons: List[str]

    details: Dict


class OIAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> OIAnalysis:

        call_oi = chain.get_call_oi()
        put_oi = chain.get_put_oi()

        call_change = chain.get_call_change_oi()
        put_change = chain.get_put_change_oi()

        # ---------------------------------------------

        resistance = max(
            call_oi,
            key=call_oi.get
        )

        support = max(
            put_oi,
            key=put_oi.get
        )

        reasons = []

        confidence = 50

        signal = "Neutral"

        # ---------------------------------------------
        # Put Writing
        # ---------------------------------------------

        max_put_change = max(
            put_change.values()
        )

        put_strike = max(
            put_change,
            key=put_change.get
        )

        if max_put_change > 0:

            reasons.append(
                f"Strong Put Writing at {put_strike}"
            )

            confidence += 15

            signal = "Bullish"

        # ---------------------------------------------
        # Call Writing
        # ---------------------------------------------

        max_call_change = max(
            call_change.values()
        )

        call_strike = max(
            call_change,
            key=call_change.get
        )

        if max_call_change > 0:

            reasons.append(
                f"Strong Call Writing at {call_strike}"
            )

            confidence += 15

            if signal == "Bullish":
                signal = "Neutral"
            else:
                signal = "Bearish"

        # ---------------------------------------------
        # Long Build-up
        # ---------------------------------------------

        long_build = 0

        for strike in chain.options:

            if (
                strike.call_change_oi > 0
                and strike.call_ltp > 0
            ):
                long_build += 1

        if long_build >= 3:

            reasons.append(
                "Call Long Build-up Detected"
            )

            confidence += 8

        # ---------------------------------------------
        # Short Covering
        # ---------------------------------------------

        short_cover = 0

        for strike in chain.options:

            if (
                strike.call_change_oi < 0
                and strike.call_ltp > 0
            ):
                short_cover += 1

        if short_cover >= 3:

            reasons.append(
                "Short Covering Detected"
            )

            confidence += 8

        # ---------------------------------------------
        # Long Unwinding
        # ---------------------------------------------

        long_unwind = 0

        for strike in chain.options:

            if (
                strike.put_change_oi < 0
                and strike.put_ltp > 0
            ):
                long_unwind += 1

        if long_unwind >= 3:

            reasons.append(
                "Long Unwinding Detected"
            )

            confidence += 8

        # ---------------------------------------------
        # Confidence
        # ---------------------------------------------

        confidence = max(
            0,
            min(100, confidence)
        )

        return OIAnalysis(

            signal=signal,

            confidence=confidence,

            support=support,

            resistance=resistance,

            reasons=reasons,

            details={

                "highest_call_oi": resistance,

                "highest_put_oi": support,

                "highest_call_change": call_strike,

                "highest_put_change": put_strike,

                "long_build_count": long_build,

                "short_cover_count": short_cover,

                "long_unwind_count": long_unwind,

            }

        )