"""
oi_analyzer.py

Trading Market AI
Options Brain V2

Open Interest Analyzer

Responsible for

• OI Support
• OI Resistance
• Call Writing
• Put Writing
• Long Build-up
• Short Build-up
• Long Unwinding
• Short Covering
• OI Wall Detection
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


# ============================================================
# Configuration
# ============================================================

CALL_WRITING_SCORE = 20
PUT_WRITING_SCORE = 20

LONG_BUILDUP_SCORE = 15
SHORT_BUILDUP_SCORE = 15

LONG_UNWIND_SCORE = 12
SHORT_COVER_SCORE = 12

SUP_RES_SCORE = 10

MAX_CONFIDENCE = 95


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class OIAnalysis:

    bias: str

    signal: str

    confidence: int

    bullish_score: int

    bearish_score: int

    support: float

    resistance: float

    reasons: List[str]

    details: Dict


# ============================================================
# Analyzer
# ============================================================

class OIAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> OIAnalysis:

        atm = chain.get_atm_strike()

        bullish_score = 0
        bearish_score = 0

        reasons = []

        details = {}

        support = None
        resistance = None

        # ===================================================
        # Support Detection
        # Highest Put OI BELOW spot
        # ===================================================

        support_candidates = [

            option

            for option in chain.get_strikes_below(chain.spot_price)

        ]

        if support_candidates:

            strongest_support = max(

                support_candidates,

                key=lambda x: x.put_oi

            )

            support = strongest_support.strike

            bullish_score += SUP_RES_SCORE

            reasons.append(

                f"Strong Put OI support at {support}"

            )

        else:

            support = atm

        # ===================================================
        # Resistance Detection
        # Highest Call OI ABOVE spot
        # ===================================================

        resistance_candidates = [

            option

            for option in chain.get_strikes_above(chain.spot_price)

        ]

        if resistance_candidates:

            strongest_resistance = max(

                resistance_candidates,

                key=lambda x: x.call_oi

            )

            resistance = strongest_resistance.strike

            bearish_score += SUP_RES_SCORE

            reasons.append(

                f"Strong Call OI resistance at {resistance}"

            )

        else:

            resistance = atm

        # ===================================================
        # Put Writing
        # ===================================================

        strongest_put_writer = max(

            chain,

            key=lambda x: x.put_change_oi

        )

        if strongest_put_writer.put_change_oi > 0:

            bullish_score += CALL_WRITING_SCORE

            reasons.append(

                f"Put Writing at {strongest_put_writer.strike}"

            )

        # ===================================================
        # Call Writing
        # ===================================================

        strongest_call_writer = max(

            chain,

            key=lambda x: x.call_change_oi

        )

        if strongest_call_writer.call_change_oi > 0:

            bearish_score += CALL_WRITING_SCORE

            reasons.append(

                f"Call Writing at {strongest_call_writer.strike}"

            )

        # ===================================================
        # Store Details
        # ===================================================

        details["atm"] = atm

        details["support"] = support

        details["resistance"] = resistance

        details["highest_call_writer"] = strongest_call_writer.strike

        details["highest_put_writer"] = strongest_put_writer.strike

        # ===================================================
        # Market Structure Detection
        # ===================================================

        long_buildup = 0
        short_buildup = 0
        long_unwinding = 0
        short_covering = 0

        call_wall_strength = 0
        put_wall_strength = 0

        # ---------------------------------------------------

        for option in chain:

            # -----------------------------------------------
            # Long Build-up
            # Price ↑ + OI ↑
            # -----------------------------------------------

            if (
                option.call_change_oi > 0
                and option.call_ltp > 0
            ):

                long_buildup += 1

            # -----------------------------------------------
            # Short Build-up
            # Put OI increasing
            # -----------------------------------------------

            if (
                option.put_change_oi > 0
                and option.put_ltp > 0
            ):

                short_buildup += 1

            # -----------------------------------------------
            # Long Unwinding
            # -----------------------------------------------

            if option.call_change_oi < 0:

                long_unwinding += 1

            # -----------------------------------------------
            # Short Covering
            # -----------------------------------------------

            if option.put_change_oi < 0:

                short_covering += 1

            # -----------------------------------------------
            # OI Wall Strength
            # -----------------------------------------------

            if option.call_oi >= 500000:

                call_wall_strength += 1

            if option.put_oi >= 500000:

                put_wall_strength += 1

        # ---------------------------------------------------
        # Score Engine
        # ---------------------------------------------------

        if long_buildup >= 3:

            bullish_score += LONG_BUILDUP_SCORE

            reasons.append(
                f"Long Build-up detected ({long_buildup} strikes)"
            )

        if short_covering >= 3:

            bullish_score += SHORT_COVER_SCORE

            reasons.append(
                f"Short Covering detected ({short_covering} strikes)"
            )

        if short_buildup >= 3:

            bearish_score += SHORT_BUILDUP_SCORE

            reasons.append(
                f"Short Build-up detected ({short_buildup} strikes)"
            )

        if long_unwinding >= 3:

            bearish_score += LONG_UNWIND_SCORE

            reasons.append(
                f"Long Unwinding detected ({long_unwinding} strikes)"
            )

        # ---------------------------------------------------
        # OI Wall Strength
        # ---------------------------------------------------

        if put_wall_strength:

            bullish_score += put_wall_strength * 2

            reasons.append(
                f"{put_wall_strength} strong Put OI wall(s)"
            )

        if call_wall_strength:

            bearish_score += call_wall_strength * 2

            reasons.append(
                f"{call_wall_strength} strong Call OI wall(s)"
            )

        # ---------------------------------------------------
        # Details
        # ---------------------------------------------------

        details.update({

            "long_buildup": long_buildup,

            "short_buildup": short_buildup,

            "long_unwinding": long_unwinding,

            "short_covering": short_covering,

            "call_wall_strength": call_wall_strength,

            "put_wall_strength": put_wall_strength,

        })

        # ===================================================
        # Final Bias
        # ===================================================

        score_difference = abs(
            bullish_score - bearish_score
        )

        if bullish_score > bearish_score:

            bias = "BULLISH"

            signal = "Bullish"

        elif bearish_score > bullish_score:

            bias = "BEARISH"

            signal = "Bearish"

        else:

            bias = "NEUTRAL"

            signal = "Neutral"

        # ===================================================
        # Confidence
        # ===================================================

        total_score = bullish_score + bearish_score

        if total_score == 0:

            confidence = 0

        else:

            confidence = int(

                min(

                    MAX_CONFIDENCE,

                    50 + score_difference

                )

            )

        # ---------------------------------------------------

        details.update({

            "bullish_score": bullish_score,

            "bearish_score": bearish_score,

            "score_difference": score_difference,

            "total_score": total_score,

        })

        # ===================================================
        # Return
        # ===================================================

        return OIAnalysis(

            bias=bias,

            signal=signal,

            confidence=confidence,

            bullish_score=bullish_score,

            bearish_score=bearish_score,

            support=support,

            resistance=resistance,

            reasons=reasons,

            details=details

        )