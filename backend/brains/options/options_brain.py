"""
options_brain.py

Master Options Brain

Combines all option analyzers into
one AI decision.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List

from .option_chain import OptionChain

from .oi_analyzer import OIAnalyzer
from .pcr_analyzer import PCRAnalyzer
from .iv_analyzer import IVAnalyzer
from .strike_analyzer import StrikeAnalyzer
from .premium_flow import PremiumFlowAnalyzer


# ------------------------------------------------------------

@dataclass
class OptionsBrainResult:

    direction: str

    confidence: int

    setup: str

    strength: str

    support: float

    resistance: float

    target: float

    stop_loss: float

    reasons: List[str]

    contradictions: List[str]

    metadata: Dict


# ------------------------------------------------------------

class OptionsBrain:

    def __init__(self):

        self.oi = OIAnalyzer()

        self.pcr = PCRAnalyzer()

        self.iv = IVAnalyzer()

        self.strike = StrikeAnalyzer()

        self.premium = PremiumFlowAnalyzer()

    # --------------------------------------------------------

    def analyze(
        self,
        chain: OptionChain
    ) -> OptionsBrainResult:

        oi = self.oi.analyze(chain)

        pcr = self.pcr.analyze(chain)

        iv = self.iv.analyze(chain)

        strike = self.strike.analyze(chain)

        premium = self.premium.analyze(chain)

        # ----------------------------------------------------
        # Voting
        # ----------------------------------------------------

        bullish = 0

        bearish = 0

        reasons = []

        contradictions = []

        analyzers = [

            ("OI", oi.signal),

            ("PCR", pcr.signal),

            ("IV", iv.signal),

            ("Strike", strike.signal),

            ("Premium", premium.signal),

        ]

        for name, signal in analyzers:

            s = signal.lower()

            if "bull" in s:

                bullish += 1

            elif "bear" in s:

                bearish += 1

        # ----------------------------------------------------

        confidence = int(

            (
                oi.confidence
                + pcr.confidence
                + iv.confidence
                + strike.confidence
                + premium.confidence
            ) / 5

        )

        # ----------------------------------------------------

        reasons.extend(oi.reasons)

        reasons.extend(pcr.reasons)

        reasons.extend(iv.reasons)

        reasons.extend(strike.reasons)

        reasons.extend(premium.reasons)

        # ----------------------------------------------------
        # Final Direction
        # ----------------------------------------------------

        if bullish >= 4:

            direction = "BUY CALL"

            setup = "Multi-Brain Bullish Confirmation"

        elif bearish >= 4:

            direction = "BUY PUT"

            setup = "Multi-Brain Bearish Confirmation"

        elif bullish > bearish:

            direction = "BUY CALL"

            setup = "Bullish Bias"

            contradictions.append(
                "Not all analyzers agree."
            )

            confidence -= 8

        elif bearish > bullish:

            direction = "BUY PUT"

            setup = "Bearish Bias"

            contradictions.append(
                "Not all analyzers agree."
            )

            confidence -= 8

        else:

            direction = "WAIT"

            setup = "Conflicting Signals"

            confidence -= 15

            contradictions.append(
                "Bullish and bearish votes are balanced."
            )

        confidence = max(0, min(100, confidence))

        # ----------------------------------------------------
        # Strength
        # ----------------------------------------------------

        if confidence >= 85:

            strength = "VERY STRONG"

        elif confidence >= 70:

            strength = "STRONG"

        elif confidence >= 55:

            strength = "MODERATE"

        else:

            strength = "WEAK"

        # ----------------------------------------------------
        # Target / Stop Loss
        # ----------------------------------------------------

        support = strike.support

        resistance = strike.resistance

        if direction == "BUY CALL":

            target = resistance

            stop_loss = support

        elif direction == "BUY PUT":

            target = support

            stop_loss = resistance

        else:

            target = chain.spot_price

            stop_loss = chain.spot_price

        # ----------------------------------------------------

        metadata = {

            "oi": asdict(oi),

            "pcr": asdict(pcr),

            "iv": asdict(iv),

            "strike": asdict(strike),

            "premium": asdict(premium)

        }

        return OptionsBrainResult(

            direction=direction,

            confidence=confidence,

            setup=setup,

            strength=strength,

            support=support,

            resistance=resistance,

            target=target,

            stop_loss=stop_loss,

            reasons=reasons,

            contradictions=contradictions,

            metadata=metadata

        )