"""
pcr_analyzer.py

Trading Market AI
Options Brain V2

Put Call Ratio Analyzer

Responsible for

• Total PCR
• ATM PCR
• Market Sentiment
• PCR Momentum
• Bias
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


# ============================================================
# Configuration
# ============================================================

STRONG_BEARISH_PCR = 0.70

BEARISH_PCR = 0.90

NEUTRAL_LOW = 0.90

NEUTRAL_HIGH = 1.10

BULLISH_PCR = 1.30

PCR_SCORE = 25

ATM_CONFIRMATION_SCORE = 15

MAX_CONFIDENCE = 95


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class PCRAnalysis:

    bias: str

    signal: str

    confidence: int

    bullish_score: int

    bearish_score: int

    pcr: float

    atm_pcr: float

    reasons: List[str]

    details: Dict


# ============================================================
# Analyzer
# ============================================================

class PCRAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> PCRAnalysis:

        bullish_score = 0

        bearish_score = 0

        reasons = []

        details = {}

        # ===================================================
        # Total PCR
        # ===================================================

        total_call_oi = chain.total_call_oi

        total_put_oi = chain.total_put_oi

        if total_call_oi == 0:

            pcr = 0.0

        else:

            pcr = total_put_oi / total_call_oi

        # ===================================================
        # ATM PCR
        # ===================================================

        atm = chain.get_atm_option()

        if (

            atm

            and

            atm.call_oi > 0

        ):

            atm_pcr = (

                atm.put_oi /

                atm.call_oi

            )

        else:

            atm_pcr = 0.0

        # ===================================================
        # PCR Classification
        # ===================================================

        if pcr < STRONG_BEARISH_PCR:

            bearish_score += PCR_SCORE

            reasons.append(

                "Very Low PCR indicates strong bearish sentiment."

            )

        elif pcr < BEARISH_PCR:

            bearish_score += PCR_SCORE - 5

            reasons.append(

                "Low PCR indicates bearish sentiment."

            )

        elif NEUTRAL_LOW <= pcr <= NEUTRAL_HIGH:

            reasons.append(

                "PCR indicates neutral positioning."

            )

        elif pcr <= BULLISH_PCR:

            bullish_score += PCR_SCORE - 5

            reasons.append(

                "High PCR indicates bullish sentiment."

            )

        else:

            bullish_score += PCR_SCORE

            reasons.append(

                "Very High PCR indicates strong bullish sentiment."

            )

        # ===================================================
        # ATM Confirmation
        # ===================================================

        if atm_pcr > 1.20:

            bullish_score += ATM_CONFIRMATION_SCORE

            reasons.append(

                "ATM PCR confirms bullish positioning."

            )

        elif atm_pcr < 0.80:

            bearish_score += ATM_CONFIRMATION_SCORE

            reasons.append(

                "ATM PCR confirms bearish positioning."

            )

        # ===================================================
        # Store Details
        # ===================================================

        details.update({

            "atm_strike": chain.get_atm_strike(),

            "total_call_oi": total_call_oi,

            "total_put_oi": total_put_oi,

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

            signal = "PCR Bullish"

        elif bearish_score > bullish_score:

            bias = "BEARISH"

            signal = "PCR Bearish"

        else:

            bias = "NEUTRAL"

            signal = "PCR Neutral"

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
        # Additional Context
        # ===================================================

        if pcr > 1.50:

            reasons.append(

                "Extreme Put dominance detected."

            )

        elif pcr < 0.60:

            reasons.append(

                "Extreme Call dominance detected."

            )

        if abs(atm_pcr - pcr) > 0.25:

            reasons.append(

                "ATM PCR differs significantly from overall PCR."

            )

        # ===================================================
        # Details
        # ===================================================

        details.update({

            "bullish_score": bullish_score,

            "bearish_score": bearish_score,

            "score_difference": score_difference,

            "total_score": total_score,

            "overall_pcr": round(pcr, 2),

            "atm_pcr": round(atm_pcr, 2),

        })

        # ===================================================
        # Return
        # ===================================================

        return PCRAnalysis(

            bias=bias,

            signal=signal,

            confidence=confidence,

            bullish_score=bullish_score,

            bearish_score=bearish_score,

            pcr=round(

                pcr,

                2

            ),

            atm_pcr=round(

                atm_pcr,

                2

            ),

            reasons=reasons,

            details=details

        )