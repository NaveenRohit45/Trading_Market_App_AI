"""
options_brain.py

Trading Market AI
Options Brain V2

Master Brain

Responsibilities

• Run all analyzers
• Collect results
• Weighted Voting
• Agreement Engine
• Final Decision
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain

from .oi_analyzer import (
    OIAnalyzer,
    OIAnalysis
)

from .pcr_analyzer import (
    PCRAnalyzer,
    PCRAnalysis
)

from .iv_analyzer import (
    IVAnalyzer,
    IVAnalysis
)

from .strike_analyzer import (
    StrikeAnalyzer,
    StrikeAnalysis
)

from .premium_flow import (
    PremiumFlowAnalyzer,
    PremiumFlowAnalysis
)

# ============================================================
# Analyzer Weights
# ============================================================

OI_WEIGHT = 0.30

PREMIUM_WEIGHT = 0.25

STRIKE_WEIGHT = 0.20

PCR_WEIGHT = 0.15

IV_WEIGHT = 0.10

MAX_CONFIDENCE = 95

# ============================================================
# Decision Thresholds
# ============================================================

BUY_THRESHOLD = 0.55

WAIT_THRESHOLD = 0.35

VERY_STRONG = 0.85

STRONG = 0.70

MODERATE = 0.55


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class OptionsBrainResult:

    direction: str

    confidence: int

    strength: str

    agreement: int

    disagreement: int

    support: float

    resistance: float

    target: float

    stop_loss: float

    reasons: List[str]

    contradictions: List[str]

    analyzer_results: Dict


# ============================================================
# Options Brain
# ============================================================

class OptionsBrain:

    def __init__(self):

        self.oi = OIAnalyzer()
        self.pcr = PCRAnalyzer()
        self.iv = IVAnalyzer()
        self.strike = StrikeAnalyzer()
        self.premium = PremiumFlowAnalyzer()

    # <-- dedent here

    def analyze(
        self,
        chain: OptionChain
    ) -> OptionsBrainResult:


        # ----------------------------------------------------
        # Execute all analyzers
        # ----------------------------------------------------

        oi = self.oi.analyze(chain)

        pcr = self.pcr.analyze(chain)

        iv = self.iv.analyze(chain)

        strike = self.strike.analyze(chain)

        premium = self.premium.analyze(chain)

        # ----------------------------------------------------
        # Store Results
        # ----------------------------------------------------

        analyzer_results = {

            "oi": oi,

            "pcr": pcr,

            "iv": iv,

            "strike": strike,

            "premium": premium

        }

        # ----------------------------------------------------
        # Agreement Counters
        # ----------------------------------------------------

        bullish_votes = 0

        bearish_votes = 0

        neutral_votes = 0

        reasons = []

        contradictions = []

        # ----------------------------------------------------
        # Count Votes
        # ----------------------------------------------------

        for result in analyzer_results.values():

            reasons.extend(result.reasons)

            if result.bias == "BULLISH":

                bullish_votes += 1

            elif result.bias == "BEARISH":

                bearish_votes += 1

            else:

                neutral_votes += 1

        agreement = max(
            bullish_votes,
            bearish_votes,
            neutral_votes
        )

        disagreement = min(

            bullish_votes,

            bearish_votes

        )

        # ===================================================
        # Weighted Voting Engine
        # ===================================================

        bullish_weight = 0.0
        bearish_weight = 0.0
        neutral_weight = 0.0

        analyzer_weights = {

            "oi": OI_WEIGHT,

            "premium": PREMIUM_WEIGHT,

            "strike": STRIKE_WEIGHT,

            "pcr": PCR_WEIGHT,

            "iv": IV_WEIGHT

        }

        # ---------------------------------------------------

        for name, result in analyzer_results.items():

            base_weight = analyzer_weights[name]

            weighted_vote = (

                                    result.confidence / 100

                            ) * base_weight

            if result.bias == "BULLISH":

                bullish_weight += weighted_vote

            elif result.bias == "BEARISH":

                bearish_weight += weighted_vote

            else:

                neutral_weight += weighted_vote

        # ---------------------------------------------------
        # Final Weighted Score
        # ---------------------------------------------------

        # weighted_difference = abs(
        #
        #     bullish_weight -
        #
        #     bearish_weight
        #
        # )

        # ---------------------------------------------------
        # Final Score Engine
        # ---------------------------------------------------

        weighted_score = max(
            bullish_weight,
            bearish_weight,
            neutral_weight
        )

        vote_score = max(
            bullish_votes,
            bearish_votes,
            neutral_votes
        ) / len(analyzer_results)

        # 60% agreement + 40% weighted confidence
        final_score = (
                vote_score * 0.60 +
                weighted_score * 0.40
        )

        agreement_ratio = round(final_score, 2)


        details = {

            "bullish_weight": round(bullish_weight, 2),

            "bearish_weight": round(bearish_weight, 2),

            "neutral_weight": round(neutral_weight, 2),

            "agreement_ratio": agreement_ratio,
            "vote_score": round(vote_score, 2),
            "weighted_score": round(weighted_score, 2),
            "final_score": round(final_score, 2),

            "bullish_votes": bullish_votes,

            "bearish_votes": bearish_votes,

            "neutral_votes": neutral_votes

        }

        # ===================================================
        # Final Decision
        # ===================================================

        # ===================================================
        # Final Decision
        # ===================================================

        # ===================================================
        # Final Decision Engine
        # ===================================================

        if bullish_votes >= 3:

            direction = "BUY CALL"

        elif bearish_votes >= 3:

            direction = "BUY PUT"

        elif neutral_votes >= 3:

            direction = "WAIT"

        elif abs(bullish_weight - bearish_weight) <= 0.08:

            direction = "WAIT"

        else:

            direction = "AVOID"

        # ===================================================
        # Strength
        # ===================================================

        if weighted_score >= VERY_STRONG:

            strength = "VERY STRONG"

        elif weighted_score >= STRONG:

            strength = "STRONG"

        elif weighted_score >= MODERATE:

            strength = "MODERATE"

        else:

            strength = "WEAK"

        # ===================================================
        # Confidence
        # ===================================================

        confidence = int(
            final_score * 100
        )

        confidence = min(
            confidence,
            MAX_CONFIDENCE
        )

        # ===================================================
        # Support / Resistance
        # ===================================================

        support = strike.support

        resistance = strike.resistance

        # ===================================================
        # Temporary Target / Stop Loss
        # ===================================================

        if direction == "BUY CALL":

            target = resistance

            stop_loss = support

        elif direction == "BUY PUT":

            target = support

            stop_loss = resistance

        else:

            target = chain.spot_price

            stop_loss = chain.spot_price

            # ===================================================
            # Smart Reason Collector
            # ===================================================

        unique_reasons = []
        seen = set()

        for result in analyzer_results.values():

            for reason in result.reasons:

                if reason not in seen:
                    unique_reasons.append(reason)

                    seen.add(reason)

        # ===================================================
        # Contradiction Engine
        # ===================================================

        contradictions = []

        bullish_modules = []
        bearish_modules = []
        neutral_modules = []

        for name, result in analyzer_results.items():

            if result.bias == "BULLISH":

                bullish_modules.append(name.upper())

            elif result.bias == "BEARISH":

                bearish_modules.append(name.upper())

            else:

                neutral_modules.append(name.upper())

        if bullish_modules and bearish_modules:
            contradictions.append(

                f"Bullish: {', '.join(bullish_modules)}"

            )

            contradictions.append(

                f"Bearish: {', '.join(bearish_modules)}"

            )

        if neutral_modules:
            contradictions.append(

                f"Neutral: {', '.join(neutral_modules)}"

            )

        # ===================================================
        # Analyzer Summary
        # ===================================================

        analyzer_summary = {

            name: {

                "bias": result.bias,

                "signal": result.signal,

                "confidence": result.confidence

            }

            for name, result in analyzer_results.items()

        }

        details["analyzer_summary"] = analyzer_summary

        # ===================================================
        # Final Return
        # ===================================================

        return OptionsBrainResult(

            direction=direction,

            confidence=confidence,

            strength=strength,

            agreement=agreement,

            disagreement=disagreement,

            support=support,

            resistance=resistance,

            target=target,

            stop_loss=stop_loss,

            reasons=unique_reasons,

            contradictions=contradictions,

            analyzer_results=analyzer_results

        )