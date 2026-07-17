"""
============================================================
ADA Trading Market AI
Confidence Engine
============================================================

Purpose

Calculates confidence based on agreement between
multiple AI brains.

This engine NEVER predicts market direction.

It only answers:

"How much should we trust the current setup?"

Author : Super Cat
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import Dict, List


# ==========================================================
# BRAIN OPINION
# ==========================================================

@dataclass
class BrainOpinion:

    name: str

    direction: str

    confidence: float

    weight: float

    reasons: List[str] = field(default_factory=list)

    contradictions: List[str] = field(default_factory=list)


# ==========================================================
# CONFIDENCE RESULT
# ==========================================================

@dataclass
class ConfidenceResult:

    confidence: float

    agreement: float

    contradiction_score: float

    supporting_brains: List[str]

    conflicting_brains: List[str]

    reasons: List[str]

    warnings: List[str]


# ==========================================================
# ENGINE
# ==========================================================

class ConfidenceEngine:

    def __init__(self):

        self.max_confidence = 95

        self.min_confidence = 0


    # ------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------

    def calculate(
        self,
        opinions: Dict[str, BrainOpinion],
    ) -> ConfidenceResult:

        if not opinions:

            return ConfidenceResult(
                confidence=0,
                agreement=0,
                contradiction_score=100,
                supporting_brains=[],
                conflicting_brains=[],
                reasons=[],
                warnings=["No active brains"],
            )

        weighted_score = 0.0

        total_weight = 0.0

        bullish = []

        bearish = []

        neutral = []

        reasons = []

        warnings = []


        # ----------------------------------------------
        # COLLECT OPINIONS
        # ----------------------------------------------

        for opinion in opinions.values():

            total_weight += opinion.weight

            weighted_score += (
                opinion.confidence
                * opinion.weight
            )

            if opinion.direction == "BULLISH":

                bullish.append(opinion.name)

            elif opinion.direction == "BEARISH":

                bearish.append(opinion.name)

            else:

                neutral.append(opinion.name)

            reasons.extend(opinion.reasons)

            warnings.extend(opinion.contradictions)


        # ----------------------------------------------
        # BASE CONFIDENCE
        # ----------------------------------------------

        if total_weight > 0:

            confidence = (
                weighted_score
                / total_weight
            )

        else:

            confidence = 0


        # ----------------------------------------------
        # AGREEMENT SCORE
        # ----------------------------------------------

        strongest = max(

            len(bullish),

            len(bearish),

            len(neutral),

        )

        agreement = (
            strongest
            / len(opinions)
        ) * 100

        # ----------------------------------------------
        # AGREEMENT BONUS
        # Give bonus only when multiple brains exist.
        # ----------------------------------------------

        if len(opinions) >= 2:

            if agreement >= 100:

                confidence += 12

            elif agreement >= 80:

                confidence += 8

            elif agreement >= 60:

                confidence += 3

        # ----------------------------------------------
        # PENALTY
        # ----------------------------------------------

        contradiction_penalty = (

            len(warnings)

            * 5

        )

        confidence -= contradiction_penalty


        # ----------------------------------------------
        # LIMITS
        # ----------------------------------------------

        confidence = max(

            self.min_confidence,

            min(

                self.max_confidence,

                confidence,

            ),

        )


        # ----------------------------------------------
        # SUPPORTING
        # ----------------------------------------------

        if len(bullish) > len(bearish):

            supporting = bullish

            conflicting = bearish

        elif len(bearish) > len(bullish):

            supporting = bearish

            conflicting = bullish

        else:

            supporting = []

            conflicting = []


        return ConfidenceResult(

            confidence=round(
                confidence,
                1,
            ),

            agreement=round(
                agreement,
                1,
            ),

            contradiction_score=round(
                contradiction_penalty,
                1,
            ),

            supporting_brains=supporting,

            conflicting_brains=conflicting,

            reasons=list(
                dict.fromkeys(reasons)
            ),

            warnings=list(
                dict.fromkeys(warnings)
            ),
        )


# ==========================================================
# FACTORY
# ==========================================================

confidence_engine = ConfidenceEngine()