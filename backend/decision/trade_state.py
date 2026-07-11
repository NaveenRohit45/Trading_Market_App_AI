"""
============================================================
ADA Trading Market AI
Trade State Definitions
============================================================

This module defines the common language used by the
Trade Decision Engine.

No trading logic should exist here.

Every brain (Price Action, Options, News, etc.)
communicates using these states.

Author : Super Cat
Version: 1.0
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


# ==========================================================
# TRADE STATE
# ==========================================================

class TradeState(str, Enum):

    WAIT = "WAIT"

    READY = "READY"

    ENTER = "ENTER"

    HOLD = "HOLD"

    BOOK_PARTIAL = "BOOK_PARTIAL"

    EXIT = "EXIT"

    AVOID = "AVOID"


# ==========================================================
# TRADE BIAS
# ==========================================================

class TradeBias(str, Enum):

    NONE = "NONE"

    CALL = "CALL"

    PUT = "PUT"


# ==========================================================
# RISK LEVEL
# ==========================================================

class RiskLevel(str, Enum):

    VERY_LOW = "VERY_LOW"

    LOW = "LOW"

    MEDIUM = "MEDIUM"

    HIGH = "HIGH"

    VERY_HIGH = "VERY_HIGH"


# ==========================================================
# MARKET CONDITION
# ==========================================================

class MarketCondition(str, Enum):

    TRENDING_BULLISH = "TRENDING_BULLISH"

    TRENDING_BEARISH = "TRENDING_BEARISH"

    SIDEWAYS = "SIDEWAYS"

    VOLATILE = "VOLATILE"

    REVERSAL = "REVERSAL"

    UNKNOWN = "UNKNOWN"


# ==========================================================
# TRADE DECISION
# ==========================================================

@dataclass
class TradeDecision:

    # ------------------------------------------------------
    # Current decision
    # ------------------------------------------------------

    state: TradeState = TradeState.WAIT

    bias: TradeBias = TradeBias.NONE

    confidence: float = 0.0

    risk: RiskLevel = RiskLevel.MEDIUM

    market_condition: MarketCondition = (
        MarketCondition.UNKNOWN
    )


    # ------------------------------------------------------
    # Entry
    # ------------------------------------------------------

    entry_price: Optional[float] = None

    entry_zone_low: Optional[float] = None

    entry_zone_high: Optional[float] = None


    # ------------------------------------------------------
    # Targets
    # ------------------------------------------------------

    target1: Optional[float] = None

    target2: Optional[float] = None

    target3: Optional[float] = None


    # ------------------------------------------------------
    # Protection
    # ------------------------------------------------------

    stop_loss: Optional[float] = None

    invalidation: Optional[float] = None


    # ------------------------------------------------------
    # Trade Management
    # ------------------------------------------------------

    expected_move_minutes: int = 0

    expected_points: float = 0.0

    reward_risk_ratio: float = 0.0


    # ------------------------------------------------------
    # Brain Output
    # ------------------------------------------------------

    reasons: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    contradictions: List[str] = field(
        default_factory=list
    )


    # ------------------------------------------------------
    # Internal Metadata
    # ------------------------------------------------------

    source_brains: List[str] = field(
        default_factory=list
    )

    timestamp: float = 0.0

    symbol: str = ""


    # ------------------------------------------------------
    # Utility
    # ------------------------------------------------------

    def to_dict(self):

        return {

            "state": self.state.value,

            "bias": self.bias.value,

            "confidence": round(
                self.confidence,
                2,
            ),

            "risk": self.risk.value,

            "market_condition":
                self.market_condition.value,

            "entry_price":
                self.entry_price,

            "entry_zone_low":
                self.entry_zone_low,

            "entry_zone_high":
                self.entry_zone_high,

            "target1":
                self.target1,

            "target2":
                self.target2,

            "target3":
                self.target3,

            "stop_loss":
                self.stop_loss,

            "invalidation":
                self.invalidation,

            "expected_move_minutes":
                self.expected_move_minutes,

            "expected_points":
                self.expected_points,

            "reward_risk_ratio":
                self.reward_risk_ratio,

            "reasons":
                self.reasons,

            "warnings":
                self.warnings,

            "contradictions":
                self.contradictions,

            "source_brains":
                self.source_brains,

            "timestamp":
                self.timestamp,

            "symbol":
                self.symbol,
        }


# ==========================================================
# HELPER
# ==========================================================

def create_default_trade(symbol: str):

    trade = TradeDecision()

    trade.symbol = symbol

    trade.state = TradeState.WAIT

    trade.bias = TradeBias.NONE

    trade.market_condition = (
        MarketCondition.UNKNOWN
    )

    return trade