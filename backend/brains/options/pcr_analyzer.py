"""
pcr_analyzer.py

Put Call Ratio Analyzer

Responsible for:
- Total PCR
- ATM PCR
- Market Bias
- Confidence Score
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


@dataclass
class PCRAnalysis:

    signal: str

    confidence: int

    pcr: float

    atm_pcr: float

    reasons: List[str]

    details: Dict


class PCRAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> PCRAnalysis:

        # ---------------------------------------------
        # Total OI
        # ---------------------------------------------

        total_call_oi = sum(
            chain.get_call_oi().values()
        )

        total_put_oi = sum(
            chain.get_put_oi().values()
        )

        if total_call_oi == 0:
            pcr = 0.0
        else:
            pcr = total_put_oi / total_call_oi

        # ---------------------------------------------
        # ATM PCR
        # ---------------------------------------------

        atm = chain.get_atm_strike()

        atm_option = chain.get_strike(atm)

        if atm_option and atm_option.call_oi > 0:
            atm_pcr = atm_option.put_oi / atm_option.call_oi
        else:
            atm_pcr = 0.0

        # ---------------------------------------------
        # Bias
        # ---------------------------------------------

        signal = "Neutral"
        confidence = 50
        reasons = []

        if pcr < 0.70:

            signal = "Strong Bearish"
            confidence = 90
            reasons.append(
                "Very low PCR indicates heavy Call dominance."
            )

        elif pcr < 0.90:

            signal = "Bearish"
            confidence = 75
            reasons.append(
                "PCR below 0.90 suggests bearish sentiment."
            )

        elif pcr <= 1.10:

            signal = "Neutral"
            confidence = 55
            reasons.append(
                "PCR near 1.0 indicates balanced positioning."
            )

        elif pcr <= 1.30:

            signal = "Bullish"
            confidence = 75
            reasons.append(
                "PCR above 1.10 suggests Put writers are stronger."
            )

        else:

            signal = "Strong Bullish"
            confidence = 90
            reasons.append(
                "Very high PCR indicates strong Put dominance."
            )

        # ---------------------------------------------
        # ATM Confirmation
        # ---------------------------------------------

        if atm_pcr > 1.20:

            confidence += 5

            reasons.append(
                "ATM PCR confirms bullish positioning."
            )

        elif atm_pcr < 0.80:

            confidence += 5

            reasons.append(
                "ATM PCR confirms bearish positioning."
            )

        confidence = max(0, min(100, confidence))

        # ---------------------------------------------

        return PCRAnalysis(

            signal=signal,

            confidence=confidence,

            pcr=round(pcr, 2),

            atm_pcr=round(atm_pcr, 2),

            reasons=reasons,

            details={

                "total_call_oi": total_call_oi,

                "total_put_oi": total_put_oi,

                "atm_strike": atm,

                "atm_call_oi": atm_option.call_oi if atm_option else 0,

                "atm_put_oi": atm_option.put_oi if atm_option else 0,

            }

        )