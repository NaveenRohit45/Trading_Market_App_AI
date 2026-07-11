"""
Trading Market AI

Options Brain Regression Test Suite

Author : Super Cat
Version : 2.0

Purpose
-------
Regression testing for OptionsBrain.

This suite validates

✓ Decision
✓ Confidence
✓ Agreement
✓ Strength
✓ Reasons
✓ Contradictions
✓ Analyzer Outputs
✓ Performance
"""

import sys
import time
import traceback
from pathlib import Path

# ============================================================
# Project Path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# Trading Imports
# ============================================================

from backend.brains.options.options_brain import (
    OptionsBrain
)

from scenarios import (

    bullish_chain,

    bearish_chain,

    sideways_chain,
    high_iv_chain,
    low_iv_chain,
    heavy_call_writing_chain,
    heavy_put_writing_chain,

    premium_bullish_chain,
    premium_bearish_chain,

    conflicting_chain,
    empty_chain,
    zero_oi_chain,

    negative_values_chain,
)

# ============================================================
# Console Formatting
# ============================================================

LINE = "=" * 75

SMALL_LINE = "-" * 75


def title(text):

    print()

    print(LINE)

    print(text.center(75))

    print(LINE)


def section(text):

    print()

    print(SMALL_LINE)

    print(text)

    print(SMALL_LINE)


# ============================================================
# Test Cases
# ============================================================

TEST_CASES = [

    {

        "name": "Bullish Market",

        "builder": bullish_chain,

        "expected": "BUY CALL"

    },

    {

        "name": "Bearish Market",

        "builder": bearish_chain,

        "expected": "BUY PUT"

    },

    {

        "name": "Sideways Market",

        "builder": sideways_chain,

        "expected": "WAIT"

    },

    {
        "name": "High IV Market",
        "builder": high_iv_chain,
        "expected": "WAIT"
    },

    {
        "name": "Low IV Market",
        "builder": low_iv_chain,
        "expected": "WAIT"
    },
    {
        "name": "Heavy Call Writing",
        "builder": heavy_call_writing_chain,
        "expected": "BUY PUT"
    },

    {
        "name": "Heavy Put Writing",
        "builder": heavy_put_writing_chain,
        "expected": "BUY CALL"
    },

    {
        "name": "Premium Bullish",
        "builder": premium_bullish_chain,
        "expected": "WAIT"
    },

    {
        "name": "Premium Bearish",
        "builder": premium_bearish_chain,
        "expected": "WAIT"
    },
    {
        "name": "Conflicting Signals",

        "builder": conflicting_chain,

        "expected": "BUY CALL"

    },

    {
        "name": "Empty Chain",
        "builder": empty_chain,
        "expected": None,
        "expect_exception": True,
    },

    {
        "name": "Zero OI",
        "builder": zero_oi_chain,
        "expected": "WAIT",
        "expect_exception": False,
    },

    {
        "name": "Negative Values",
        "builder": negative_values_chain,
        "expected": None,
        "expect_exception": True,
    },
]

# ============================================================
# Validation
# ============================================================


def validate_result(result):

    errors = []

    if result.direction not in (

        "BUY CALL",

        "BUY PUT",

        "WAIT",

        "AVOID"

    ):

        errors.append(

            "Invalid Direction"

        )

    if not (

        0 <= result.confidence <= 95

    ):

        errors.append(

            "Invalid Confidence"

        )

    if result.strength not in (

        "VERY STRONG",

        "STRONG",

        "MODERATE",

        "WEAK"

    ):

        errors.append(

            "Invalid Strength"

        )

    if result.support <= 0:

        errors.append(

            "Invalid Support"

        )

    if result.resistance <= 0:

        errors.append(

            "Invalid Resistance"

        )

    if result.target <= 0:

        errors.append(

            "Invalid Target"

        )

    if result.stop_loss <= 0:

        errors.append(

            "Invalid Stop Loss"

        )

    if not isinstance(

        result.reasons,

        list

    ):

        errors.append(

            "Reasons must be list"

        )

    if not isinstance(

        result.contradictions,

        list

    ):

        errors.append(

            "Contradictions must be list"

        )

    if not isinstance(

        result.analyzer_results,

        dict

    ):

        errors.append(

            "Analyzer results must be dict"

        )

    return errors


# ============================================================
# Analyzer Printer
# ============================================================

def print_analyzer_summary(result):

    section("Analyzer Summary")

    print(

        f"{'Analyzer':<15}"

        f"{'Bias':<12}"

        f"{'Confidence':<12}"

        f"{'Signal'}"

    )

    print(SMALL_LINE)

    for name, analyzer in result.analyzer_results.items():

        print(

            f"{name.upper():<15}"

            f"{analyzer.bias:<12}"

            f"{analyzer.confidence:<12}"

            f"{analyzer.signal}"

        )

# ============================================================
# Single Scenario Runner
# ============================================================

def run_single_test(test_case):

    name = test_case["name"]

    expected = test_case["expected"]

    builder = test_case["builder"]

    title(f"Scenario : {name}")

    # --------------------------------------------------------
    # Build Scenario
    # --------------------------------------------------------

    chain = builder()

    print(f"Symbol        : {chain.symbol}")
    print(f"Expiry        : {chain.expiry}")
    print(f"Spot Price    : {chain.spot_price}")
    print(f"ATM Strike    : {chain.get_atm_strike()}")

    # --------------------------------------------------------
    # Run Brain
    # --------------------------------------------------------

    start = time.perf_counter()

    result = OptionsBrain().analyze(chain)

    execution_time = (

        time.perf_counter() -

        start

    ) * 1000

    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    section("Decision")

    print(f"Expected      : {expected}")

    print(f"Actual        : {result.direction}")

    print(f"Confidence    : {result.confidence}")

    print(f"Strength      : {result.strength}")

    print()

    print(f"Agreement     : {result.agreement}")

    print(f"Disagreement  : {result.disagreement}")

    # --------------------------------------------------------
    # Levels
    # --------------------------------------------------------

    section("Levels")

    print(f"Support       : {result.support}")

    print(f"Resistance    : {result.resistance}")

    print(f"Target        : {result.target}")

    print(f"Stop Loss     : {result.stop_loss}")

    # --------------------------------------------------------
    # Reasons
    # --------------------------------------------------------

    section("Reasons")

    if result.reasons:

        for reason in result.reasons:

            print(f"✓ {reason}")

    else:

        print("No Reasons")

    # --------------------------------------------------------
    # Contradictions
    # --------------------------------------------------------

    section("Contradictions")

    if result.contradictions:

        for item in result.contradictions:

            print(f"• {item}")

    else:

        print("None")

    # --------------------------------------------------------
    # Analyzer Summary
    # --------------------------------------------------------

    print_analyzer_summary(result)

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    errors = validate_result(result)

    section("Validation")

    if errors:

        print("FAILED")

        for error in errors:

            print(f"✗ {error}")

        passed = False

    else:

        print("PASSED")

        passed = (

            result.direction ==

            expected

        )

    # --------------------------------------------------------
    # Scenario Result
    # --------------------------------------------------------

    section("Scenario Result")

    if passed:

        print("✅ PASS")

    else:

        print("❌ FAIL")

    print()

    print(

        f"Execution Time : "

        f"{execution_time:.2f} ms"

    )

    return {

        "scenario": name,

        "expected": expected,

        "actual": result.direction,

        "passed": passed,

        "execution_time": execution_time,

        "confidence": result.confidence,

        "strength": result.strength,

        "agreement": result.agreement

    }

# ============================================================
# Regression Runner
# ============================================================

def run_regression():

    title("Trading Market AI - Options Brain Regression Suite")

    total_tests = len(TEST_CASES)

    passed = 0

    failed = 0

    execution_times = []

    report = []

    for test_case in TEST_CASES:

        try:

            result = run_single_test(test_case)

            if result["passed"]:

                passed += 1

            else:

                failed += 1

            report.append(result)

            execution_times.append(

                result["execution_time"]

            )


        except Exception as e:

            if test_case.get("expect_exception", False):
                print("✅ Expected Exception")

                passed += 1

                report.append({

                    "scenario": test_case["name"],

                    "expected": "Exception",

                    "actual": "Exception",

                    "passed": True

                })

                continue

            failed += 1

            report.append({

                "scenario": test_case["name"],

                "expected": test_case.get("expected"),

                "actual": type(e).__name__,

                "passed": False

            })

            print(f"\n❌ UNEXPECTED EXCEPTION\n{e}")

            continue

    # --------------------------------------------------------
    # Final Report
    # --------------------------------------------------------

    title("Regression Report")

    print(

        f"{'Scenario':<30}"

        f"{'Expected':<15}"

        f"{'Actual':<15}"

        f"{'Status'}"

    )

    print(SMALL_LINE)

    for item in report:

        status = "PASS" if item["passed"] else "FAIL"

        print(

            f"{item['scenario']:<30}"

            f"{str(item['expected']):<15}"

            f"{item['actual']:<15}"

            f"{status}"

        )

    print()

    print(SMALL_LINE)

    print(f"Total Tests      : {total_tests}")

    print(f"Passed           : {passed}")

    print(f"Failed           : {failed}")

    success_rate = (

        (passed / total_tests) * 100

        if total_tests

        else 0

    )

    print(f"Success Rate     : {success_rate:.2f}%")

    if execution_times:

        avg = sum(execution_times) / len(execution_times)

        fastest = min(execution_times)

        slowest = max(execution_times)

    else:

        avg = fastest = slowest = 0

    print()

    print(f"Average Time     : {avg:.2f} ms")

    print(f"Fastest          : {fastest:.2f} ms")

    print(f"Slowest          : {slowest:.2f} ms")

    print()

    if failed == 0:

        print("🎉 ALL SCENARIOS PASSED")

    else:

        print("⚠️ SOME SCENARIOS FAILED")

    print()

    print(LINE)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    try:

        run_regression()

    except KeyboardInterrupt:

        print()

        print("Interrupted by user.")

    except Exception:

        print()

        print("❌ Regression Runner Failed")

        traceback.print_exc()