"""
============================================================
Trading Market AI
Trade Decision Engine Test
============================================================
"""

from backend.decision.trade_decision_engine import (
    DecisionContext,
    trade_decision_engine,
)

# ==========================================================
# HELPER
# ==========================================================

def print_result(title, decision):

    print("\n" + "=" * 75)
    print(title)
    print("=" * 75)

    print("STATE           :", decision.state.value)
    print("BIAS            :", decision.bias.value)
    print("CONFIDENCE      :", decision.confidence)
    print("RISK            :", decision.risk.value)
    print("MARKET          :", decision.market_condition.value)

    print("\nENTRY")

    print("Entry           :", decision.entry_price)
    print("Entry Zone      :", decision.entry_zone_low,
          "-", decision.entry_zone_high)

    print("Stop Loss       :", decision.stop_loss)

    print("Target 1        :", decision.target1)
    print("Target 2        :", decision.target2)

    print("Expected Points :", decision.expected_points)

    print("Reward / Risk   :", decision.reward_risk_ratio)

    print("\nREASONS")

    if decision.reasons:

        for r in decision.reasons:

            print("  +", r)

    else:

        print("  None")

    print("\nWARNINGS")

    if decision.warnings:

        for w in decision.warnings:

            print("  -", w)

    else:

        print("  None")

    print("\nCONTRADICTIONS")

    if decision.contradictions:

        for c in decision.contradictions:

            print("  -", c)

    else:

        print("  None")

    print("\nSOURCE BRAINS")

    print(decision.source_brains)


# ==========================================================
# TEST 1
# ==========================================================

ctx = DecisionContext(

    symbol="NIFTY",

    price=24240,

    support=24220,

    resistance=24280,

    atr=10,

    price_action={

        "direction": "BULLISH",

        "confidence": 92,

        "setup": "CALL_SETUP",

        "reasons": [

            "Strong bullish structure",

            "Momentum increasing",

        ],

        "contradictions": [],

    },

)

decision = trade_decision_engine.decide(ctx)

print_result(

    "TEST 1 - STRONG CALL",

    decision,

)


# ==========================================================
# TEST 2
# ==========================================================

ctx = DecisionContext(

    symbol="NIFTY",

    price=24240,

    support=24220,

    resistance=24280,

    atr=10,

    price_action={

        "direction": "BEARISH",

        "confidence": 90,

        "setup": "PUT_SETUP",

        "reasons": [

            "Breakdown",

        ],

        "contradictions": [],

    },

)

decision = trade_decision_engine.decide(ctx)

print_result(

    "TEST 2 - STRONG PUT",

    decision,

)


# ==========================================================
# TEST 3
# ==========================================================

ctx = DecisionContext(

    symbol="NIFTY",

    price=24240,

    support=24220,

    resistance=24280,

    atr=10,

    price_action={

        "direction": "NEUTRAL",

        "confidence": 30,

        "setup": "WAIT",

        "reasons": [],

        "contradictions": [

            "Choppy Market",

        ],

    },

)

decision = trade_decision_engine.decide(ctx)

print_result(

    "TEST 3 - WAIT",

    decision,

)


# ==========================================================
# TEST 4
# ==========================================================

ctx = DecisionContext(

    symbol="NIFTY",

    price=24240,

    support=24239,

    resistance=24242,

    atr=40,

    price_action={

        "direction": "BULLISH",

        "confidence": 65,

        "setup": "CALL_SETUP",

        "reasons": [

            "Weak setup",

        ],

        "contradictions": [

            "High volatility",

        ],

    },

)

decision = trade_decision_engine.decide(ctx)

print_result(

    "TEST 4 - READY / AVOID",

    decision,

)


print("\n")
print("=" * 75)
print("TRADE DECISION ENGINE TEST COMPLETED")
print("=" * 75)