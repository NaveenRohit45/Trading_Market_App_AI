"""
iv_analyzer.py

Trading Market AI
Options Brain V2

Implied Volatility Analyzer

Responsible for

• Average Call IV
• Average Put IV
• ATM IV
• IV Skew
• Volatility Regime
• Premium Buying Risk
• Premium Selling Opportunity
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


# ============================================================
# Configuration
# ============================================================

LOW_IV = 12.0

NORMAL_IV = 18.0

HIGH_IV = 25.0

VERY_HIGH_IV = 35.0

HIGH_SKEW = 2.0

IV_SCORE = 20

SKEW_SCORE = 10

RISK_SCORE = 15

MAX_CONFIDENCE = 95


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class IVAnalysis:

    bias: str

    signal: str

    confidence: int

    bullish_score: int

    bearish_score: int

    average_call_iv: float

    average_put_iv: float

    atm_iv: float

    iv_skew: float

    volatility_regime: str

    reasons: List[str]

    details: Dict


# ============================================================
# Analyzer
# ============================================================

class IVAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> IVAnalysis:

        bullish_score = 0

        bearish_score = 0

        reasons = []

        details = {}

        avg_call_iv = chain.average_call_iv

        avg_put_iv = chain.average_put_iv

        atm_option = chain.get_atm_option()

        # ===================================================
        # ATM IV
        # ===================================================

        if atm_option:

            atm_iv = (

                atm_option.call_iv +

                atm_option.put_iv

            ) / 2

        else:

            atm_iv = 0.0

        # ===================================================
        # IV Skew
        # ===================================================

        iv_skew = avg_put_iv - avg_call_iv

        # ===================================================
        # Volatility Regime
        # ===================================================

        if atm_iv <= LOW_IV:

            volatility_regime = "LOW"

            bullish_score += IV_SCORE

            reasons.append(

                "Low IV. Premium buying is relatively cheap."

            )

        elif atm_iv <= NORMAL_IV:

            volatility_regime = "NORMAL"

            bullish_score += IV_SCORE // 2

            bearish_score += IV_SCORE // 2

            reasons.append(

                "Normal implied volatility."

            )

        elif atm_iv <= HIGH_IV:

            volatility_regime = "HIGH"

            bearish_score += IV_SCORE

            reasons.append(

                "High IV. Premiums are expensive."

            )

        else:

            volatility_regime = "VERY_HIGH"

            bearish_score += IV_SCORE + 5

            reasons.append(

                "Very High IV. Premium selling may be favorable."

            )

        # ===================================================
        # IV Skew
        # ===================================================

        if iv_skew >= HIGH_SKEW:

            bullish_score += SKEW_SCORE

            reasons.append(

                "Put IV significantly higher than Call IV."

            )

        elif iv_skew <= -HIGH_SKEW:

            bearish_score += SKEW_SCORE

            reasons.append(

                "Call IV significantly higher than Put IV."

            )

        # ===================================================
        # Premium Risk
        # ===================================================

        if volatility_regime in ("HIGH", "VERY_HIGH"):

            bearish_score += RISK_SCORE

            reasons.append(

                "Premium buying carries elevated risk."

            )

        elif volatility_regime == "LOW":

            bullish_score += RISK_SCORE

            reasons.append(

                "Premium buying risk is relatively low."

            )

        # ===================================================
        # Store Details
        # ===================================================

        details.update({

            "average_call_iv": round(
                avg_call_iv,
                2
            ),

            "average_put_iv": round(
                avg_put_iv,
                2
            ),

            "atm_iv": round(
                atm_iv,
                2
            ),

            "iv_skew": round(
                iv_skew,
                2
            ),

            "volatility_regime": volatility_regime

        })

        # ===================================================
        # Volatility Opportunity
        # ===================================================

        if volatility_regime == "LOW":

            bullish_score += 5

            reasons.append(
                "Low volatility favors premium buyers."
            )

        elif volatility_regime == "NORMAL":

            reasons.append(
                "Balanced volatility environment."
            )

        elif volatility_regime == "HIGH":

            bearish_score += 5

            reasons.append(
                "High volatility favors premium sellers."
            )

        elif volatility_regime == "VERY_HIGH":

            bearish_score += 10

            reasons.append(
                "Very high volatility may result in IV crush."
            )

        # ===================================================
        # IV Balance
        # ===================================================

        iv_difference = abs(iv_skew)

        if iv_difference < 1.0:

            reasons.append(
                "Call and Put IV are well balanced."
            )

        elif iv_difference < HIGH_SKEW:

            reasons.append(
                "Moderate IV skew detected."
            )

        else:

            reasons.append(
                "Strong IV skew detected."
            )

        # ===================================================
        # Volatility Strength
        # ===================================================

        if atm_iv < LOW_IV:

            volatility_strength = "VERY_LOW"

        elif atm_iv < NORMAL_IV:

            volatility_strength = "LOW"

        elif atm_iv < HIGH_IV:

            volatility_strength = "NORMAL"

        elif atm_iv < VERY_HIGH_IV:

            volatility_strength = "HIGH"

        else:

            volatility_strength = "EXTREME"

        details.update({

            "volatility_strength": volatility_strength,

            "iv_difference": round(
                iv_difference,
                2
            )

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

            signal = "IV Bullish"

        elif bearish_score > bullish_score:

            bias = "BEARISH"

            signal = "IV Bearish"

        else:

            bias = "NEUTRAL"

            signal = "IV Neutral"

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

        return IVAnalysis(

            bias=bias,

            signal=signal,

            confidence=confidence,

            bullish_score=bullish_score,

            bearish_score=bearish_score,

            average_call_iv=round(
                avg_call_iv,
                2
            ),

            average_put_iv=round(
                avg_put_iv,
                2
            ),

            atm_iv=round(
                atm_iv,
                2
            ),

            iv_skew=round(
                iv_skew,
                2
            ),

            volatility_regime=volatility_regime,

            reasons=reasons,

            details=details

        )