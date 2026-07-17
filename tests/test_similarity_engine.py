"""
Trading Market AI V2

Similarity Engine Tests

Author : Super Cat
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.brains.learning.models import MarketFeatures
from backend.brains.learning.similarity_engine import SimilarityEngine


# ==========================================================
# Helper
# ==========================================================

def create_features(**kwargs) -> MarketFeatures:

    defaults = dict(
        symbol="NIFTY",
        timeframe="3m",
        decision="BUY",
        confidence=90.0,
        price_action="BULLISH",
        live_market="BULLISH",
        options="BULLISH",
        global_market="BULLISH",
        trend="UPTREND",
        atr_bucket="HIGH",
        vix_bucket="LOW",
        support_distance=20.0,
        resistance_distance=80.0,
        market_session="OPEN",
        confidence_bucket="VERY_HIGH",
        brain_agreement=5,
        extra={},
    )

    defaults.update(kwargs)

    return MarketFeatures(**defaults)


# ==========================================================
# Perfect Match
# ==========================================================

def test_perfect_match():

    engine = SimilarityEngine()

    current = create_features()

    historical = create_features()

    result = engine.compare(current, historical)

    print("\nPerfect Match")
    print(result)

    assert result.score == 100.0

    assert result.matched_features == result.total_features

    assert result.missed == []

    assert result.partial_matches == {}


# ==========================================================
# Completely Different
# ==========================================================

def test_complete_mismatch():

    engine = SimilarityEngine()

    current = create_features()

    historical = create_features(
        decision="SELL",
        confidence=10,
        price_action="BEARISH",
        live_market="BEARISH",
        options="BEARISH",
        global_market="BEARISH",
        trend="DOWNTREND",
        atr_bucket="VERY_LOW",
        vix_bucket="VERY_HIGH",
        market_session="CLOSE",
        confidence_bucket="VERY_LOW",
        brain_agreement=0,
    )

    result = engine.compare(current, historical)

    print("\nComplete Mismatch")
    print(result)

    assert result.score < 20

    assert len(result.missed) > 0


# ==========================================================
# ATR Partial Match
# ==========================================================

def test_atr_partial_match():

    engine = SimilarityEngine()

    current = create_features(
        atr_bucket="HIGH",
    )

    historical = create_features(
        atr_bucket="VERY_HIGH",
    )

    result = engine.compare(current, historical)

    print("\nATR Partial")
    print(result)

    assert "atr_bucket" in result.partial_matches

    assert result.partial_matches["atr_bucket"] == 0.75


# ==========================================================
# VIX Partial Match
# ==========================================================

def test_vix_partial_match():

    engine = SimilarityEngine()

    current = create_features(
        vix_bucket="LOW",
    )

    historical = create_features(
        vix_bucket="MEDIUM",
    )

    result = engine.compare(current, historical)

    print("\nVIX Partial")
    print(result)

    assert "vix_bucket" in result.partial_matches

    assert result.partial_matches["vix_bucket"] == 0.75


# ==========================================================
# Confidence Partial Match
# ==========================================================

def test_confidence_partial():

    engine = SimilarityEngine()

    current = create_features(
        confidence=90,
    )

    historical = create_features(
        confidence=88,
    )

    result = engine.compare(current, historical)

    print("\nConfidence Partial")
    print(result)

    assert "confidence" in result.partial_matches

    assert result.partial_matches["confidence"] > 0.95


# ==========================================================
# Dynamic Weight
# ==========================================================

def test_dynamic_weight():

    engine = SimilarityEngine()

    normal = engine._weight("trend")

    engine.dynamic_weights["trend"] = 2.0

    boosted = engine._weight("trend")

    print("\nDynamic Weight")

    print(normal, boosted)

    assert boosted == normal * 2


# ==========================================================
# Unknown Feature
# ==========================================================

def test_unknown_feature():

    engine = SimilarityEngine()

    try:

        engine._weight("UNKNOWN")

        assert False

    except KeyError:

        assert True


# ==========================================================
# Runner
# ==========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("SIMILARITY ENGINE TESTS")
    print("=" * 70)

    test_perfect_match()
    test_complete_mismatch()
    test_atr_partial_match()
    test_vix_partial_match()
    test_confidence_partial()
    test_dynamic_weight()
    test_unknown_feature()

    print("\n")
    print("=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)