"""
premium_flow.py

Trading Market AI
Options Brain V2

Premium Flow Analyzer

Responsible for

• Premium Flow
• Volume Flow
• Buyer / Seller Pressure
• Smart Money Detection
• Flow Strength
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


# ============================================================
# Configuration
# ============================================================

PREMIUM_SCORE = 25

VOLUME_SCORE = 20

SMART_MONEY_SCORE = 15

FLOW_DOMINANCE_SCORE = 10

MAX_CONFIDENCE = 95


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class PremiumFlowAnalysis:

    bias: str

    signal: str

    confidence: int

    bullish_score: int

    bearish_score: int

    call_premium: float

    put_premium: float

    call_volume: int

    put_volume: int

    premium_ratio: float

    volume_ratio: float

    reasons: List[str]

    details: Dict


# ============================================================
# Analyzer
# ============================================================

class PremiumFlowAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> PremiumFlowAnalysis:

        bullish_score = 0

        bearish_score = 0

        reasons = []

        details = {}

        call_premium = chain.total_call_premium

        put_premium = chain.total_put_premium

        call_volume = chain.total_call_volume

        put_volume = chain.total_put_volume

        # ===================================================
        # Premium Ratio
        # ===================================================

        total_premium = call_premium + put_premium

        if total_premium > 0:

            premium_ratio = call_premium / total_premium

        else:

            premium_ratio = 0.50

        # ===================================================
        # Volume Ratio
        # ===================================================

        total_volume = call_volume + put_volume

        if total_volume > 0:

            volume_ratio = call_volume / total_volume

        else:

            volume_ratio = 0.50

        # ===================================================
        # Premium Dominance
        # ===================================================

        if premium_ratio >= 0.65:

            bullish_score += PREMIUM_SCORE

            reasons.append(
                "Call premium dominates."
            )


        elif premium_ratio <= 0.35:

            bearish_score += PREMIUM_SCORE

            reasons.append(
                "Put premium dominates."
            )

        else:

            reasons.append(
                "Premium flow is balanced."
            )

        # ===================================================
        # Volume Dominance
        # ===================================================

        if volume_ratio >= 0.60:

            bullish_score += VOLUME_SCORE

            reasons.append(
                "Call volume dominates."
            )

        elif volume_ratio <= 0.40:

            bearish_score += VOLUME_SCORE

            reasons.append(
                "Put volume dominates."
            )

        else:

            reasons.append(
                "Volume flow is balanced."
            )

        # ===================================================
        # Buyer / Seller Pressure
        # ===================================================

        flow_gap = abs(

            premium_ratio -

            volume_ratio

        )

        if flow_gap >= 0.10:

            if premium_ratio > volume_ratio:

                bullish_score += FLOW_DOMINANCE_SCORE

                reasons.append(

                    "Premium flow stronger than volume flow."

                )

            else:

                bearish_score += FLOW_DOMINANCE_SCORE

                reasons.append(

                    "Volume flow stronger than premium flow."

                )

        else:

            reasons.append(

                "Premium and volume flow are aligned."

            )

        # ===================================================
        # Smart Money Detection
        # ===================================================

        if (

            premium_ratio > 0.70

            and

            volume_ratio > 0.60

        ):

            bullish_score += SMART_MONEY_SCORE

            reasons.append(
                "Possible institutional Call buying."
            )

        elif (

            premium_ratio < 0.40

            and

            volume_ratio < 0.40

        ):

            bearish_score += SMART_MONEY_SCORE

            reasons.append(
                "Possible institutional Put buying."
            )

        # ===================================================
        # Store Details
        # ===================================================

        details.update({

            "call_premium": round(
                call_premium,
                2
            ),

            "put_premium": round(
                put_premium,
                2
            ),

            "call_volume": call_volume,

            "put_volume": put_volume,

            "premium_ratio": round(
                premium_ratio,
                3
            ),

            "volume_ratio": round(
                volume_ratio,
                3
            )

        })

        # ===================================================
        # Flow Strength
        # ===================================================

        flow_difference = abs(
            premium_ratio - volume_ratio
        )

        if flow_difference >= 0.25:

            flow_strength = "VERY_STRONG"

        elif flow_difference >= 0.15:

            flow_strength = "STRONG"

        elif flow_difference >= 0.08:

            flow_strength = "MODERATE"

        else:

            flow_strength = "WEAK"

        reasons.append(
            f"Flow Strength : {flow_strength}"
        )

        # ===================================================
        # Smart Money
        # ===================================================

        if bullish_score > bearish_score:

            smart_money = "CALL BUYERS"

        elif bearish_score > bullish_score:

            smart_money = "PUT BUYERS"

        else:

            smart_money = "NEUTRAL"

        reasons.append(
            f"Smart Money : {smart_money}"
        )

        # ===================================================
        # Premium Pressure
        # ===================================================

        premium_difference = abs(
            call_premium -
            put_premium
        )

        volume_difference = abs(
            call_volume -
            put_volume
        )

        details.update({

            "flow_strength": flow_strength,

            "smart_money": smart_money,

            "premium_difference": round(
                premium_difference,
                2
            ),

            "volume_difference": volume_difference

        })

        # ===================================================
        # Bias
        # ===================================================

        score_difference = abs(

            bullish_score -

            bearish_score

        )

        if bullish_score > bearish_score:

            bias = "BULLISH"

            signal = "Premium Flow Bullish"

        elif bearish_score > bullish_score:

            bias = "BEARISH"

            signal = "Premium Flow Bearish"

        else:

            bias = "NEUTRAL"

            signal = "Premium Flow Neutral"

        # ===================================================
        # Confidence
        # ===================================================

        total_score = bullish_score + bearish_score

        if total_score == 0:

            confidence = 50

        else:

            confidence = int(

                (

                    max(

                        bullish_score,

                        bearish_score

                    )

                    /

                    total_score

                )

                * 100

            )

            confidence = min(

                confidence,

                MAX_CONFIDENCE

            )

        # ===================================================
        # Final Details
        # ===================================================

        details.update({

            "bullish_score": bullish_score,

            "bearish_score": bearish_score,

            "score_difference": score_difference,

            "total_score": total_score,

            "confidence": confidence

        })

        # ===================================================
        # Return
        # ===================================================

        return PremiumFlowAnalysis(

            bias=bias,

            signal=signal,

            confidence=confidence,

            bullish_score=bullish_score,

            bearish_score=bearish_score,

            call_premium=round(
                call_premium,
                2
            ),

            put_premium=round(
                put_premium,
                2
            ),

            call_volume=call_volume,

            put_volume=put_volume,

            premium_ratio=round(
                premium_ratio,
                3
            ),

            volume_ratio=round(
                volume_ratio,
                3
            ),

            reasons=reasons,

            details=details

        )