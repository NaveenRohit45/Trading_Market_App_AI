"""
iv_analyzer.py

Implied Volatility Analyzer

Responsible for:
- Average IV
- ATM IV
- IV Skew
- High / Low Volatility
- Premium Buying Risk
"""

from dataclasses import dataclass
from typing import Dict, List

from .option_chain import OptionChain

# -------------------------------------------------------
# Configurable Thresholds
# -------------------------------------------------------

LOW_IV = 12.0
NORMAL_IV = 18.0
HIGH_IV = 25.0

HIGH_SKEW = 2.0

# -------------------------------------------------------


@dataclass
class IVAnalysis:

    signal: str

    confidence: int

    average_call_iv: float

    average_put_iv: float

    atm_iv: float

    iv_skew: float

    reasons: List[str]

    details: Dict


class IVAnalyzer:

    def analyze(
        self,
        chain: OptionChain
    ) -> IVAnalysis:

        reasons = []

        confidence = 50

        call_ivs = [
            option.call_iv
            for option in chain.options
            if option.call_iv > 0
        ]

        put_ivs = [
            option.put_iv
            for option in chain.options
            if option.put_iv > 0
        ]

        avg_call_iv = (
            sum(call_ivs) / len(call_ivs)
            if call_ivs else 0.0
        )

        avg_put_iv = (
            sum(put_ivs) / len(put_ivs)
            if put_ivs else 0.0
        )

        atm = chain.get_atm_strike()

        atm_option = chain.get_strike(atm)

        if atm_option:

            atm_iv = (
                atm_option.call_iv +
                atm_option.put_iv
            ) / 2

        else:

            atm_iv = 0.0

        iv_skew = avg_put_iv - avg_call_iv

        # -------------------------------------------------
        # Volatility Regime
        # -------------------------------------------------

        signal = "Neutral"

        if atm_iv <= LOW_IV:

            signal = "Low IV"

            confidence += 20

            reasons.append(
                "Low implied volatility. Premium buying is relatively cheaper."
            )

        elif atm_iv <= NORMAL_IV:

            signal = "Normal IV"

            confidence += 10
