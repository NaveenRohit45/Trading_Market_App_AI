"""
============================================================
Trading Market AI
Global Market Brain Tests
============================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.brains.global_market.global_market_brain import (
    GlobalMarketBrain,
)


# ============================================================
# TEST SCENARIOS
# ============================================================

SCENARIOS = [

    {
        "name": "STRONG BULLISH",

        "gift_previous_close": 25000,
        "gift_current_price": 25200,

        "dow_change": 1.45,
        "nasdaq_change": 2.10,
        "sp500_change": 1.35,

        "nikkei_change": 1.20,
        "hang_seng_change": 1.10,
        "shanghai_change": 0.85,

        "india_vix": 12.5,

        "usd_inr": 82.40,

        "gold_change": -1.20,
        "crude_change": -2.30,
    },

    {
        "name": "BULLISH",

        "gift_previous_close": 25000,
        "gift_current_price": 25080,

        "dow_change": 0.70,
        "nasdaq_change": 0.65,
        "sp500_change": 0.55,

        "nikkei_change": 0.60,
        "hang_seng_change": 0.40,
        "shanghai_change": 0.30,

        "india_vix": 15,

        "usd_inr": 83.20,

        "gold_change": -0.30,
        "crude_change": -0.60,
    },

    {
        "name": "NEUTRAL",

        "gift_previous_close": 25000,
        "gift_current_price": 25005,

        "dow_change": 0.10,
        "nasdaq_change": -0.10,
        "sp500_change": 0.05,

        "nikkei_change": 0.00,
        "hang_seng_change": -0.20,
        "shanghai_change": 0.10,

        "india_vix": 18,

        "usd_inr": 85.10,

        "gold_change": 0.20,
        "crude_change": 0.10,
    },

    {
        "name": "BEARISH",

        "gift_previous_close": 25000,
        "gift_current_price": 24880,

        "dow_change": -0.90,
        "nasdaq_change": -0.70,
        "sp500_change": -0.80,

        "nikkei_change": -0.65,
        "hang_seng_change": -0.50,
        "shanghai_change": -0.45,

        "india_vix": 22,

        "usd_inr": 87.10,

        "gold_change": 1.10,
        "crude_change": 1.80,
    },

    {
        "name": "STRONG BEARISH",

        "gift_previous_close": 25000,
        "gift_current_price": 24680,

        "dow_change": -2.30,
        "nasdaq_change": -3.10,
        "sp500_change": -2.60,

        "nikkei_change": -2.10,
        "hang_seng_change": -1.90,
        "shanghai_change": -1.70,

        "india_vix": 31,

        "usd_inr": 89.20,

        "gold_change": 2.20,
        "crude_change": 3.40,
    },

]


# ============================================================
# TEST
# ============================================================

def run():

    print("\n")
    print("=" * 70)
    print("GLOBAL MARKET BRAIN")
    print("=" * 70)

    for case in SCENARIOS:

        analysis = GlobalMarketBrain.analyze(

            gift_previous_close=case["gift_previous_close"],
            gift_current_price=case["gift_current_price"],

            dow_change=case["dow_change"],
            nasdaq_change=case["nasdaq_change"],
            sp500_change=case["sp500_change"],

            nikkei_change=case["nikkei_change"],
            hang_seng_change=case["hang_seng_change"],
            shanghai_change=case["shanghai_change"],

            india_vix=case["india_vix"],

            usd_inr=case["usd_inr"],

            gold_change=case["gold_change"],
            crude_change=case["crude_change"],

        )

        print("\n")
        print("=" * 70)
        print(case["name"])
        print("=" * 70)

        print("Overall Sentiment :", analysis.overall_sentiment)
        print("Market Bias       :", analysis.market_bias)
        print("Market Score      :", analysis.market_score)

        print()

        print("Gift Nifty        :", analysis.gift_nifty)
        print("US Market         :", analysis.us_market)
        print("Asian Market      :", analysis.asian_market)
        print("India VIX         :", analysis.vix)
        print("Currency          :", analysis.currency)
        print("Commodity         :", analysis.commodity)

        print()

        print("Market Score      :", analysis.market_score)
        print("Confidence        :", analysis.confidence)
        print("Agreement         :", analysis.agreement)

        print("Reasons")

        for reason in analysis.reasons:

            print(" •", reason)

        print()

        print("Warnings")

        if analysis.warnings:

            for warning in analysis.warnings:

                print(" •", warning)

        else:

            print(" None")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run()