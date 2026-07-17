"""
============================================================
Trading Market AI
Live Market Brain Tests
============================================================
"""
import sys
import json
import inspect
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, date
from dataclasses import dataclass

from backend.brains.live_market.live_market_brain import (
    LiveMarketBrain,
)


# ============================================================
# Dummy Candle
# ============================================================

@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float


# ============================================================
# Helper
# ============================================================

def generate_uptrend():

    candles = []

    price = 25000

    for _ in range(30):

        candles.append(

            Candle(

                open=price,

                high=price + 25,

                low=price - 10,

                close=price + 20,

            )

        )

        price += 20

    return candles


# ============================================================
# Test
# ============================================================

def test_live_market_brain():

    candles = generate_uptrend()

    analysis = LiveMarketBrain.analyze(

        now=datetime(2026, 7, 16, 9, 25),

        yesterday_close=25000,

        today_open=25120,

        candles=candles,

        current_volume=2500000,

        average_volume=1000000,

        tick_rate=95,

        nifty_change=0.82,

        sensex_change=0.71,

        banknifty_change=1.10,

        advance_decline_ratio=2.1,

        today=date(2026, 7, 16),

        weekly_expiry=date(2026, 7, 23),

        monthly_expiry=date(2026, 7, 30),

    )

    print("\n============================")
    print("LIVE MARKET BRAIN")
    print("============================")

    print("Market State :", analysis.market_state)
    print("Bias         :", analysis.market_bias)
    # print("Confidence   :", analysis.confidence)
    print("Market Score :", analysis.market_score)

    print()

    print("Session      :", analysis.session)
    print("Trend        :", analysis.trend)
    print("Volatility   :", analysis.volatility)
    print("Gap          :", analysis.gap)
    print("Liquidity    :", analysis.liquidity)
    print("Strength     :", analysis.market_strength)
    print("Expiry       :", analysis.expiry_type)

    print()

    print("Strategy     :", analysis.recommended_strategy)

    print()

    print("Reasons")

    for reason in analysis.reasons:

        print(" •", reason)

    print()

    print("Warnings")

    for warning in analysis.warnings:

        print(" •", warning)

    print()

    print("Details")

    for key, value in analysis.details.items():
        print(f"{key}: {value}")

# ============================================================
# Run Test
# ============================================================

if __name__ == "__main__":
    test_live_market_brain()