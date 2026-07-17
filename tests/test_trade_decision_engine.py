"""
Trading Market AI

Trade Decision Engine Regression Test

Tests:

✓ CALL setup
✓ PUT setup
✓ WAIT state
✓ Low confidence
✓ High confidence
✓ Entry / Stop / Target
✓ Reward Risk Ratio
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.decision.trade_decision_engine import (
    DecisionContext,
    trade_decision_engine,
)


# ==========================================================
# Pretty Printer
# ==========================================================

LINE = "=" * 80


def show(title):

    print()
    print(LINE)
    print(title)
    print(LINE)


def print_decision(d):

    print("State        :", d.state.value)
    print("Bias         :", d.bias.value)

    print("Confidence   :", d.confidence)

    print("Risk         :", d.risk.value)

    print()

    print("Entry        :", d.entry_price)

    print("Entry Zone   :", d.entry_zone_low, "-", d.entry_zone_high)

    print("Stop Loss    :", d.stop_loss)

    print("Target 1     :", d.target1)

    print("Target 2     :", d.target2)

    print("RR Ratio     :", d.reward_risk_ratio)

    print()

    print("Reasons")

    for r in d.reasons:

        print("  ✓", r)

    if d.warnings:

        print()

        print("Warnings")

        for w in d.warnings:

            print("  ⚠", w)


# ==========================================================
# Scenario Builder
# ==========================================================

def build_context(

        direction,

        setup,

        confidence,

        price=25000,

        support=24950,

        resistance=25080,

        atr=20,

):

    return DecisionContext(

        symbol="NIFTY",

        price=price,

        support=support,

        resistance=resistance,

        atr=atr,

        timestamp=0,

        price_action={

            "direction": direction,

            "confidence": confidence,

            "setup": setup,

            "reasons": [

                "Regression Test"

            ],

            "contradictions": []

        }

    )


# ==========================================================
# CALL
# ==========================================================

show("CALL SETUP")

ctx = build_context(

    direction="BULLISH",

    setup="CALL_SETUP",

    confidence=90,

)

decision = trade_decision_engine.decide(ctx)

print_decision(decision)


# ==========================================================
# PUT
# ==========================================================

show("PUT SETUP")

ctx = build_context(

    direction="BEARISH",

    setup="PUT_SETUP",

    confidence=90,

)

decision = trade_decision_engine.decide(ctx)

print_decision(decision)


# ==========================================================
# WAIT
# ==========================================================

show("WAIT")

ctx = build_context(

    direction="NEUTRAL",

    setup="WAIT",

    confidence=10,

)

decision = trade_decision_engine.decide(ctx)

print_decision(decision)


# ==========================================================
# LOW CONFIDENCE
# ==========================================================

show("LOW CONFIDENCE")

ctx = build_context(

    direction="BULLISH",

    setup="CALL_SETUP",

    confidence=40,

)

decision = trade_decision_engine.decide(ctx)

print_decision(decision)


# ==========================================================
# READY
# ==========================================================

show("READY")

ctx = build_context(

    direction="BULLISH",

    setup="CALL_SETUP",

    confidence=75,

)

decision = trade_decision_engine.decide(ctx)

print_decision(decision)


# ==========================================================
# ENTER
# ==========================================================

show("ENTER")

ctx = build_context(

    direction="BULLISH",

    setup="CALL_SETUP",

    confidence=95,

)

decision = trade_decision_engine.decide(ctx)

print_decision(decision)

print()
print(LINE)
print("Regression Finished")
print(LINE)