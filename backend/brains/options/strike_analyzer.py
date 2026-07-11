"""
strike_analyzer.py

Trading Market AI
Options Brain V2

Strike Analyzer

Responsible for

• Support Detection
• Resistance Detection
• OI Wall Analysis
• Max Pain
• Breakout Probability
• Strike Ranking
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain


# ============================================================
# Configuration
# ============================================================

SUP_RES_SCORE = 20

OI_WALL_THRESHOLD = 500000

VERY_STRONG_WALL = 1000000

BREAKOUT_SCORE = 20

MAX_CONFIDENCE = 95


# ============================================================
# Result
# ============================================================

@dataclass(slots=True)
class StrikeAnalysis:

    bias: str

    signal: str

    confidence: int

    bullish_score: int

    bearish_score: int

    support: float

    resistance: float

    support_levels: List[float]

    resistance_levels: List[float]

    max_pain: float

    breakout_probability: float

    reasons: List[str]

    details: Dict


# ============================================================
# Analyzer
# ============================================================

class StrikeAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> StrikeAnalysis:

        atm = chain.get_atm_strike()

        bullish_score = 0

        bearish_score = 0

        reasons = []

        details = {}

        support = atm

        resistance = atm

        support_levels = []

        resistance_levels = []

        # ===================================================
        # Support Levels
        # ===================================================

        support_candidates = sorted(

            chain.get_strikes_below(chain.spot_price),

            key=lambda x: x.put_oi,

            reverse=True

        )

        if support_candidates:

            support_levels = [

                option.strike

                for option in support_candidates[:3]

            ]

            support = support_levels[0]

            bullish_score += SUP_RES_SCORE

            reasons.append(

                f"Primary Support : {support}"

            )

        # ===================================================
        # Resistance Levels
        # ===================================================

        resistance_candidates = sorted(

            chain.get_strikes_above(chain.spot_price),

            key=lambda x: x.call_oi,

            reverse=True

        )

        if resistance_candidates:

            resistance_levels = [

                option.strike

                for option in resistance_candidates[:3]

            ]

            resistance = resistance_levels[0]

            bearish_score += SUP_RES_SCORE

            reasons.append(

                f"Primary Resistance : {resistance}"

            )

        # ===================================================
        # OI Wall Ranking
        # ===================================================

        strong_call_walls = []

        strong_put_walls = []

        for option in chain:

            if option.call_oi >= OI_WALL_THRESHOLD:

                strong_call_walls.append(

                    {

                        "strike": option.strike,

                        "oi": option.call_oi

                    }

                )

            if option.put_oi >= OI_WALL_THRESHOLD:

                strong_put_walls.append(

                    {

                        "strike": option.strike,

                        "oi": option.put_oi

                    }

                )

        strong_call_walls.sort(

            key=lambda x: x["oi"],

            reverse=True

        )

        strong_put_walls.sort(

            key=lambda x: x["oi"],

            reverse=True

        )

        if strong_put_walls:

            bullish_score += len(strong_put_walls) * 2

            reasons.append(

                f"{len(strong_put_walls)} Put OI Wall(s)"

            )

        if strong_call_walls:

            bearish_score += len(strong_call_walls) * 2

            reasons.append(

                f"{len(strong_call_walls)} Call OI Wall(s)"

            )

        # ===================================================
        # Store Details
        # ===================================================

        details.update({

            "atm": atm,

            "support_levels": support_levels,

            "resistance_levels": resistance_levels,

            "strong_call_walls": strong_call_walls,

            "strong_put_walls": strong_put_walls,

        })

        # ===================================================
        # Approximate Max Pain
        # ===================================================

        max_pain = atm

        highest_combined_oi = 0

        for option in chain:

            combined_oi = option.call_oi + option.put_oi

            if combined_oi > highest_combined_oi:

                highest_combined_oi = combined_oi

                max_pain = option.strike

        reasons.append(
            f"Approximate Max Pain at {max_pain}"
        )

        # ===================================================
        # Support / Resistance Distance
        # ===================================================

        support_distance = max(
            0,
            chain.spot_price - support
        )

        resistance_distance = max(
            0,
            resistance - chain.spot_price
        )

        details["support_distance"] = round(
            support_distance,
            2
        )

        details["resistance_distance"] = round(
            resistance_distance,
            2
        )

        # ===================================================
        # Breakout Probability
        # ===================================================

        total_wall_strength = (
            bullish_score +
            bearish_score
        )

        if total_wall_strength == 0:

            breakout_probability = 50.0

        else:

            breakout_probability = round(

                (
                    abs(
                        bullish_score -
                        bearish_score
                    )
                    /
                    total_wall_strength
                ) * 100,

                2

            )

        # ===================================================
        # Wall Strength Classification
        # ===================================================

        def classify_wall(oi: int) -> str:

            if oi >= VERY_STRONG_WALL:
                return "VERY_STRONG"

            if oi >= 750000:
                return "STRONG"

            if oi >= OI_WALL_THRESHOLD:
                return "MEDIUM"

            return "WEAK"

        details["call_wall_strength"] = [

            {

                "strike": wall["strike"],

                "strength": classify_wall(
                    wall["oi"]
                ),

                "oi": wall["oi"]

            }

            for wall in strong_call_walls

        ]

        details["put_wall_strength"] = [

            {

                "strike": wall["strike"],

                "strength": classify_wall(
                    wall["oi"]
                ),

                "oi": wall["oi"]

            }

            for wall in strong_put_walls

        ]

        # ===================================================
        # Bias
        # ===================================================

        score_difference = abs(

            bullish_score -

            bearish_score

        )

        if bullish_score > bearish_score:

            bias = "BULLISH"

            signal = "Strike Bullish"

        elif bearish_score > bullish_score:

            bias = "BEARISH"

            signal = "Strike Bearish"

        else:

            bias = "NEUTRAL"

            signal = "Strike Neutral"

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
        # Store Details
        # ===================================================

        details.update({

            "bullish_score": bullish_score,

            "bearish_score": bearish_score,

            "score_difference": score_difference,

            "total_score": total_score,

            "max_pain": max_pain,

            "breakout_probability": breakout_probability

        })

        # ===================================================
        # Return
        # ===================================================

        return StrikeAnalysis(

            bias=bias,

            signal=signal,

            confidence=confidence,

            bullish_score=bullish_score,

            bearish_score=bearish_score,

            support=support,

            resistance=resistance,

            support_levels=support_levels,

            resistance_levels=resistance_levels,

            max_pain=max_pain,

            breakout_probability=breakout_probability,

            reasons=reasons,

            details=details

        )