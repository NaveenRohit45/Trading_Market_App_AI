"""
============================================================
Live Market Brain Models
Trading Market AI
Author : Super Cat
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ============================================================
# Market Session
# ============================================================

class MarketSession(str, Enum):
    PRE_MARKET = "PRE_MARKET"
    OPENING = "OPENING"
    MORNING = "MORNING"
    MIDDAY = "MIDDAY"
    AFTERNOON = "AFTERNOON"
    CLOSING = "CLOSING"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"


# ============================================================
# Trend
# ============================================================

class MarketTrend(str, Enum):
    STRONG_UPTREND = "STRONG_UPTREND"
    UPTREND = "UPTREND"
    SIDEWAYS = "SIDEWAYS"
    DOWNTREND = "DOWNTREND"
    STRONG_DOWNTREND = "STRONG_DOWNTREND"
    REVERSAL_UP = "REVERSAL_UP"
    REVERSAL_DOWN = "REVERSAL_DOWN"


# ============================================================
# Market Bias
# ============================================================

class MarketBias(str, Enum):
    STRONG_BULLISH = "STRONG_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


# ============================================================
# Volatility
# ============================================================

class VolatilityLevel(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


# ============================================================
# Gap
# ============================================================

class GapType(str, Enum):
    GAP_UP = "GAP_UP"
    GAP_DOWN = "GAP_DOWN"
    FLAT = "FLAT"


# ============================================================
# Liquidity
# ============================================================

class LiquidityLevel(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


# ============================================================
# Market Strength
# ============================================================

class MarketStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


# ============================================================
# Expiry Type
# ============================================================

class ExpiryType(str, Enum):
    NORMAL = "NORMAL"
    WEEKLY_EXPIRY = "WEEKLY_EXPIRY"
    MONTHLY_EXPIRY = "MONTHLY_EXPIRY"
    SPECIAL_EXPIRY = "SPECIAL_EXPIRY"


# ============================================================
# Recommended Strategy
# ============================================================

class RecommendedStrategy(str, Enum):
    TREND_FOLLOWING = "TREND_FOLLOWING"
    BREAKOUT = "BREAKOUT"
    SCALPING = "SCALPING"
    MEAN_REVERSION = "MEAN_REVERSION"
    RANGE_TRADING = "RANGE_TRADING"
    REVERSAL = "REVERSAL"
    NO_TRADE = "NO_TRADE"


# ============================================================
# Live Market Analysis
# ============================================================

@dataclass(slots=True)
class LiveMarketAnalysis:
    """
    Final output of the Live Market Brain.

    This object is passed into the Confidence Engine.
    """

    # Overall AI Decision
    market_state: str = "UNKNOWN"
    market_bias: MarketBias = MarketBias.NEUTRAL
    market_score: float = 0.0

    # Individual Analyzer Results
    session: MarketSession = MarketSession.CLOSED
    trend: MarketTrend = MarketTrend.SIDEWAYS
    volatility: VolatilityLevel = VolatilityLevel.NORMAL
    gap: GapType = GapType.FLAT
    liquidity: LiquidityLevel = LiquidityLevel.NORMAL
    market_strength: MarketStrength = MarketStrength.MODERATE
    expiry_type: ExpiryType = ExpiryType.NORMAL

    # Suggested Trading Style
    recommended_strategy: RecommendedStrategy = (
        RecommendedStrategy.NO_TRADE
    )

    # Explainability
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Extra analyzer-specific information
    details: dict[str, Any] = field(default_factory=dict)