from backend.models import Candle
from backend.brains.price_action_brain import PriceActionBrain


brain = PriceActionBrain()


# ==========================================================
# CANDLE BUILDER
# ==========================================================

def make_candles(
    prices,
    symbol="NIFTY",
    interval_seconds=60,
):

    candles = []

    for i, price in enumerate(prices):

        previous_price = (
            prices[i - 1]
            if i > 0
            else price
        )

        candle_open = previous_price
        candle_close = price

        candles.append(
            Candle(
                symbol=symbol,
                start_ts=(
                    1000
                    + (
                        i
                        * interval_seconds
                    )
                ),
                open=candle_open,
                high=max(
                    candle_open,
                    candle_close,
                ) + 2,
                low=min(
                    candle_open,
                    candle_close,
                ) - 2,
                close=candle_close,
                volume=1000 + (i * 100),
            )
        )

    return candles


# ==========================================================
# PRICE SERIES
# ==========================================================

BULLISH = [
    24000,
    24005,
    24010,
    24016,
    24022,
    24030,
    24038,
    24047,
    24057,
    24068,
    24080,
    24093,
    24107,
    24122,
    24138,
    24155,
    24173,
    24192,
    24212,
    24233,
]


BEARISH = list(
    reversed(
        BULLISH
    )
)


CHOPPY = [
    24000,
    24010,
    24003,
    24012,
    24005,
    24014,
    24006,
    24013,
    24007,
    24015,
    24008,
    24014,
    24009,
    24013,
    24008,
    24012,
    24007,
    24011,
    24006,
    24010,
]


# ==========================================================
# MULTI-TIMEFRAME BUILDER
# ==========================================================

def build_timeframes(
    one_minute,
    two_minute,
    three_minute,
    five_minute,
):

    return {
        "1m": make_candles(
            one_minute,
            interval_seconds=60,
        ),

        "2m": make_candles(
            two_minute,
            interval_seconds=120,
        ),

        "3m": make_candles(
            three_minute,
            interval_seconds=180,
        ),

        "5m": make_candles(
            five_minute,
            interval_seconds=300,
        ),
    }


# ==========================================================
# TEST RUNNER
# ==========================================================

def run_test(
    name,
    candles,
    expected_setup,
):

    print("\n")
    print("=" * 75)
    print(name)
    print("=" * 75)

    result = brain.analyze(
        symbol="NIFTY",
        candles=candles,
    )


    print(
        "STATUS       :",
        result["status"],
    )

    print(
        "DIRECTION    :",
        result["direction"],
    )

    print(
        "CONFIDENCE   :",
        result["confidence"],
    )

    print(
        "SCORE        :",
        result["score"],
    )

    print(
        "STRUCTURE    :",
        result["structure"],
    )

    print(
        "SETUP        :",
        result["setup"],
    )

    print(
        "INVALIDATION :",
        result["invalidation"],
    )


    print("\nTIMEFRAMES:")

    for timeframe, tf_result in (
        result["timeframes"].items()
    ):

        print(
            f"  {timeframe:<3}",
            "|",
            f"{tf_result['direction']:<8}",
            "| SCORE:",
            f"{tf_result['score']:>4}",
            "| STRUCTURE:",
            tf_result["structure"],
            "| CANDLES:",
            tf_result["candle_count"],
        )


    print("\nAGREEMENT:")

    agreement = result.get(
        "agreement",
        {},
    )

    print(
        "  Bullish:",
        agreement.get(
            "bullish",
            [],
        ),
    )

    print(
        "  Bearish:",
        agreement.get(
            "bearish",
            [],
        ),
    )

    print(
        "  Neutral:",
        agreement.get(
            "neutral",
            [],
        ),
    )


    print("\nREASONS:")

    for reason in result[
        "reasons"
    ]:

        print(
            "  +",
            reason,
        )


    print("\nCONTRADICTIONS:")

    if result["contradictions"]:

        for contradiction in result[
            "contradictions"
        ]:

            print(
                "  -",
                contradiction,
            )

    else:

        print(
            "  None"
        )


    print("\nEXPECTED SETUP :", expected_setup)
    print(
        "ACTUAL SETUP   :",
        result["setup"],
    )


    if result["setup"] == expected_setup:

        print(
            "RESULT         : ✅ PASS"
        )

        return True

    else:

        print(
            "RESULT         : ❌ FAIL"
        )

        return False


# ==========================================================
# TEST 1
# ALL TIMEFRAMES BULLISH
# ==========================================================

test_1 = run_test(

    name=(
        "TEST 1 — ALL TIMEFRAMES BULLISH"
    ),

    candles=build_timeframes(
        one_minute=BULLISH,
        two_minute=BULLISH,
        three_minute=BULLISH,
        five_minute=BULLISH,
    ),

    expected_setup="CALL_SETUP",
)


# ==========================================================
# TEST 2
# ALL TIMEFRAMES BEARISH
# ==========================================================

test_2 = run_test(

    name=(
        "TEST 2 — ALL TIMEFRAMES BEARISH"
    ),

    candles=build_timeframes(
        one_minute=BEARISH,
        two_minute=BEARISH,
        three_minute=BEARISH,
        five_minute=BEARISH,
    ),

    expected_setup="PUT_SETUP",
)


# ==========================================================
# TEST 3
# 1M BULLISH BUT 5M BEARISH
# SHOULD WAIT
# ==========================================================

test_3 = run_test(

    name=(
        "TEST 3 — FAST BULLISH / 5M BEARISH CONFLICT"
    ),

    candles=build_timeframes(
        one_minute=BULLISH,
        two_minute=BULLISH,
        three_minute=BEARISH,
        five_minute=BEARISH,
    ),

    expected_setup="WAIT",
)


# ==========================================================
# TEST 4
# CHOPPY MARKET
# ==========================================================

test_4 = run_test(

    name=(
        "TEST 4 — CHOPPY MULTI-TIMEFRAME MARKET"
    ),

    candles=build_timeframes(
        one_minute=CHOPPY,
        two_minute=CHOPPY,
        three_minute=CHOPPY,
        five_minute=CHOPPY,
    ),

    expected_setup="WAIT",
)


# ==========================================================
# FINAL SUMMARY
# ==========================================================

results = [
    test_1,
    test_2,
    test_3,
    test_4,
]


passed = sum(
    results
)


print("\n")
print("=" * 75)
print("FINAL TEST SUMMARY")
print("=" * 75)

print(
    f"PASSED: {passed} / {len(results)}"
)


if passed == len(results):

    print(
        "🧠 MULTI-TIMEFRAME PRICE ACTION BRAIN: ALL TESTS PASSED"
    )

else:

    print(
        "⚠️ PRICE ACTION BRAIN NEEDS CORRECTION"
    )