"""
strike_analyzer.py

Strike Analysis

Responsible for:
- ATM Strike
- Support
- Resistance
- Max Pain
- OI Walls
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


@dataclass
class StrikeAnalysis:

    signal: str

    confidence: int

    atm: float

    support: float

    resistance: float

    max_pain: float

    reasons: List[str]

    details: Dict


class StrikeAnalyzer:

    # -----------------------------------------------------

    def analyze(
        self,
        chain: OptionChain
    ) -> StrikeAnalysis:

        atm = chain.get_atm_strike()

        call_oi = chain.get_call_oi()

        put_oi = chain.get_put_oi()

        strikes = chain.get_all_strikes()

        # -------------------------------------------------
        # Strongest Support
        # -------------------------------------------------

        support = max(
            put_oi,
            key=put_oi.get
        )

        # -------------------------------------------------
        # Strongest Resistance
        # -------------------------------------------------

        resistance = max(
            call_oi,
            key=call_oi.get
        )

        # -------------------------------------------------
        # Nearest Support Below ATM
        # -------------------------------------------------

        support_candidates = [
            s for s in strikes
            if s <= atm
        ]

        if support_candidates:

            nearest_support = max(
                support_candidates
            )

        else:

            nearest_support = support

        # -------------------------------------------------
        # Nearest Resistance Above ATM
        # -------------------------------------------------

        resistance_candidates = [
            s for s in strikes
            if s >= atm
        ]

        if resistance_candidates:

            nearest_resistance = min(
                resistance_candidates
            )

        else:

            nearest_resistance = resistance

        # -------------------------------------------------
        # Max Pain (simple version)
        # -------------------------------------------------

        max_pain = max(

            strikes,

            key=lambda strike:
                call_oi.get(strike, 0)
                +
                put_oi.get(strike, 0)

        )

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        confidence = 60

        reasons = []

        signal = "Neutral"

        if atm < resistance:

            reasons.append(
                "Price below major Call OI wall."
            )

            confidence += 10

        if atm > support:

            reasons.append(
                "Price above major Put OI support."
            )

            confidence += 10

        if abs(atm - max_pain) <= 50:

            reasons.append(
                "Spot trading near Max Pain."
            )

            confidence += 10

        if resistance - support <= 100:

            reasons.append(
                "Market inside narrow option range."
            )

            confidence += 5

        if atm > max_pain:

            signal = "Bullish"

        elif atm < max_pain:

            signal = "Bearish"

        else:

            signal = "Neutral"

        confidence = min(100, confidence)

        # -------------------------------------------------

        return StrikeAnalysis(

            signal=signal,

            confidence=confidence,

            atm=atm,

            support=nearest_support,

            resistance=nearest_resistance,

            max_pain=max_pain,

            reasons=reasons,

            details={

                "major_support": support,

                "major_resistance": resistance,

                "nearest_support": nearest_support,

                "nearest_resistance": nearest_resistance,

                "total_strikes": len(strikes)

            }

        )