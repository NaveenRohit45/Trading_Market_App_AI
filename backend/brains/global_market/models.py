"""
============================================================
Global Market Brain Models
Trading Market AI
Author : Super Cat
============================================================

Shared models for the Global Market Brain.

Every analyzer returns one of these dataclasses.

The final GlobalMarketAnalysis is consumed by the
Confidence Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


# ============================================================
# OVERALL SENTIMENT
# ============================================================

class GlobalSentiment(Enum):

    STRONG_BULLISH = "STRONG_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


# ============================================================
# US MARKET
# ============================================================

class USMarketSentiment(Enum):

    STRONG_POSITIVE = "STRONG_POSITIVE"
    POSITIVE = "POSITIVE"
    MIXED = "MIXED"
    NEGATIVE = "NEGATIVE"
    STRONG_NEGATIVE = "STRONG_NEGATIVE"


# ============================================================
# ASIAN MARKET
# ============================================================

class AsianMarketSentiment(Enum):

    STRONG_POSITIVE = "STRONG_POSITIVE"
    POSITIVE = "POSITIVE"
    MIXED = "MIXED"
    NEGATIVE = "NEGATIVE"
    STRONG_NEGATIVE = "STRONG_NEGATIVE"


# ============================================================
# GIFT NIFTY
# ============================================================

class GiftNiftyTrend(Enum):

    GAP_UP = "GAP_UP"
    FLAT = "FLAT"
    GAP_DOWN = "GAP_DOWN"


# ============================================================
# INDIA VIX
# ============================================================

class VIXLevel(Enum):

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    PANIC = "PANIC"


# ============================================================
# USD INR
# ============================================================

class CurrencyStrength(Enum):

    STRONG_RUPEE = "STRONG_RUPEE"
    RUPEE = "RUPEE"
    NEUTRAL = "NEUTRAL"
    WEAK_RUPEE = "WEAK_RUPEE"
    VERY_WEAK_RUPEE = "VERY_WEAK_RUPEE"


# ============================================================
# COMMODITIES
# ============================================================

class CommoditySentiment(Enum):

    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"


# ============================================================
# MARKET BIAS
# ============================================================

class GlobalMarketBias(Enum):

    STRONG_BULLISH = "STRONG_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


# ============================================================
# US MARKET ANALYSIS
# ============================================================

@dataclass(slots=True)
class USMarketAnalysis:

    sentiment: USMarketSentiment

    dow_change: float

    nasdaq_change: float

    sp500_change: float

    score: float

    reason: str


# ============================================================
# ASIAN MARKET ANALYSIS
# ============================================================

@dataclass(slots=True)
class AsianMarketAnalysis:

    sentiment: AsianMarketSentiment

    nikkei_change: float

    hang_seng_change: float

    shanghai_change: float

    score: float

    reason: str


# ============================================================
# GIFT NIFTY
# ============================================================

@dataclass(slots=True)
class GiftNiftyAnalysis:

    trend: GiftNiftyTrend

    points: float

    percent: float

    score: float

    reason: str


# ============================================================
# INDIA VIX
# ============================================================

@dataclass(slots=True)
class VIXAnalysis:

    level: VIXLevel

    value: float

    score: float

    reason: str


# ============================================================
# USD INR
# ============================================================

@dataclass(slots=True)
class CurrencyAnalysis:

    strength: CurrencyStrength

    usd_inr: float

    score: float

    reason: str


# ============================================================
# COMMODITIES
# ============================================================

@dataclass(slots=True)
class CommodityAnalysis:

    sentiment: CommoditySentiment

    gold_change: float

    crude_change: float

    score: float

    reason: str


# ============================================================
# FINAL ANALYSIS
# ============================================================

@dataclass(slots=True)
class GlobalMarketAnalysis:

    overall_sentiment: GlobalSentiment

    market_bias: GlobalMarketBias

    market_score: float

    us_market: USMarketSentiment

    asian_market: AsianMarketSentiment

    gift_nifty: GiftNiftyTrend

    vix: VIXLevel

    currency: CurrencyStrength

    commodity: CommoditySentiment

    confidence: float

    agreement: float

    positive_factors: List[str] = field(default_factory=list)

    negative_factors: List[str] = field(default_factory=list)

    reasons: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    details: Dict = field(default_factory=dict)