"""
============================================================
ADA Trading Market AI
Risk Manager
============================================================

Capital Protection Engine

This module NEVER predicts market direction.

It protects trades.

Author : Super Cat
Version : 1.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


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
# RISK PROFILE
# ==========================================================

@dataclass
class RiskProfile:

    atr_multiplier: float = 1.5

    minimum_rr: float = 1.8

    target1_rr: float = 1.5

    target2_rr: float = 2.5

    max_allowed_risk: float = 95

    max_daily_loss_percent: float = 3

    max_consecutive_losses: int = 3

    max_position_size: float = 1.0

    minimum_position_size: float = 0.25


# ==========================================================
# RISK RESULT
# ==========================================================

@dataclass
class RiskAssessment:

    can_trade: bool = False

    risk_level: RiskLevel = RiskLevel.MEDIUM

    confidence: float = 0.0

    # ------------------------------------------------------
    # ADVANCED RISK
    # ------------------------------------------------------

    risk_score: float = 0.0

    position_size: float = 1.0

    capital_allocation: float = 0.0

    volatility_score: float = 0.0

    confidence_adjustment: float = 0.0


    entry: Optional[float] = None

    stop_loss: Optional[float] = None

    target1: Optional[float] = None

    target2: Optional[float] = None

    # ------------------------------------------------------
    # LIVE TRADE
    # ------------------------------------------------------

    current_stop: Optional[float] = None

    trail_stop: Optional[float] = None

    booked_partial: bool = False

    breakeven_active: bool = False

    profit_locked: bool = False

    current_profit_points: float = 0.0

    trade_status: str = "WAITING"


    risk_points: float = 0.0

    reward_points: float = 0.0

    reward_risk_ratio: float = 0.0

    # ------------------------------------------------------
    # EXIT MANAGEMENT
    # ------------------------------------------------------

    trade_completed: bool = False

    exit_reason: str = ""

    exit_price: Optional[float] = None

    target1_hit: bool = False

    target2_hit: bool = False

    stop_hit: bool = False

    emergency_exit: bool = False




    reasons: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )


# ==========================================================
# RISK MANAGER
# ==========================================================

class RiskManager:

    def __init__(self):

        self.profile = RiskProfile()

        self.trailing_multiplier = 1.2

        self.breakeven_trigger = 1.0

        self.partial_trigger = 1.5

        self.profit_lock_trigger = 2.0


    # ------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------

    def assess(

        self,

        direction,

        price,

        support,

        resistance,

        atr,

        confidence,

    ):

        result = RiskAssessment()

        print("=" * 60)
        # print("RISK MANAGER INPUT")
        print("=" * 60)

        print("Direction :", direction)
        print("Price     :", price)
        print("Support   :", support)
        print("Resistance:", resistance)
        print("ATR       :", atr)
        print("Confidence:", confidence)
        print()

        result.entry = price

        result.confidence = confidence


        # ----------------------------------------------
        # STOP LOSS
        # ----------------------------------------------

        stop = self._calculate_stop(

            direction,

            price,

            support,

            resistance,

            atr,

        )

        result.stop_loss = stop


        # ----------------------------------------------
        # TARGETS
        # ----------------------------------------------

        t1, t2 = self._calculate_targets(

            direction,

            price,

            stop,

        )

        result.target1 = t1

        result.target2 = t2

        print("ENTRY :", result.entry)
        print("STOP  :", result.stop_loss)
        print("T1    :", result.target1)
        print("T2    :", result.target2)
        print("=" * 60)


        # ----------------------------------------------
        # REWARD / RISK
        # ----------------------------------------------

        rr = self._reward_risk(

            price,

            stop,

            t2,

        )

        result.reward_risk_ratio = rr

        volatility = self._volatility_score(
            atr,
            price,
        )

        result.volatility_score = volatility

        result.position_size = (
            self._position_size(
                confidence,
                rr,
            )
        )

        result.risk_score = (
            self._risk_score(
                confidence,
                rr,
                volatility,
            )
        )


        # ----------------------------------------------
        # RISK LEVEL
        # ----------------------------------------------

        result.risk_level = self._risk_level(

            rr,

            confidence,

        )


        # ----------------------------------------------
        # CAN TRADE
        # ----------------------------------------------

        if (
                rr >= self.profile.minimum_rr
                and confidence >= 60
                and result.risk_score < 60
        ):

            if result.position_size < 1:
                result.warnings.append(
                    "Reduce position size"
                )

            if volatility > 0.8:
                result.warnings.append(
                    "High market volatility"
                )

            if confidence < 70:
                result.warnings.append(
                    "Weak confidence"
                )
            result.can_trade = True

            result.reasons.append(

                "Reward/Risk acceptable"

            )

        else:

            result.can_trade = False

            result.warnings.append(

                "Poor reward/risk"

            )


        return result


    # ======================================================
    # STOP LOSS
    # ======================================================

    def _calculate_stop(

        self,

        direction,

        price,

        support,

        resistance,

        atr,

    ):

        atr_stop = (

            atr

            * self.profile.atr_multiplier

        )


        if direction == "BULLISH":

            if support is not None:

                return min(

                    support,

                    price - atr_stop,

                )

            return price - atr_stop


        if direction == "BEARISH":

            if resistance is not None:

                return max(

                    resistance,

                    price + atr_stop,

                )

            return price + atr_stop


        return price


    # ======================================================
    # TARGETS
    # ======================================================

    def _calculate_targets(

        self,

        direction,

        entry,

        stop,

    ):

        risk = abs(

            entry - stop

        )


        if direction == "BULLISH":

            target1 = (

                entry

                + (

                    risk

                    * self.profile.target1_rr

                )

            )

            target2 = (

                entry

                + (

                    risk

                    * self.profile.target2_rr

                )

            )

        else:

            target1 = (

                entry

                - (

                    risk

                    * self.profile.target1_rr

                )

            )

            target2 = (

                entry

                - (

                    risk

                    * self.profile.target2_rr

                )

            )


        return (

            round(target1,2),

            round(target2,2),

        )


    # ======================================================
    # RR
    # ======================================================

    def _reward_risk(

        self,

        entry,

        stop,

        target,

    ):

        risk = abs(

            entry-stop

        )

        reward = abs(

            target-entry

        )


        if risk == 0:

            return 0


        return round(

            reward/risk,

            2,

        )


    # ======================================================
    # RISK LEVEL
    # ======================================================

    def _risk_level(

        self,

        rr,

        confidence,

    ):

        if rr >= 3 and confidence >= 85:

            return RiskLevel.VERY_LOW


        if rr >= 2.5 and confidence >= 75:

            return RiskLevel.LOW


        if rr >= 2:

            return RiskLevel.MEDIUM


        if rr >= 1.5:

            return RiskLevel.HIGH


        return RiskLevel.VERY_HIGH

    # ======================================================
    # VOLATILITY SCORE
    # ======================================================

    def _volatility_score(
            self,
            atr,
            price,
    ):

        if price <= 0:
            return 100

        percent = (
                          atr
                          / price
                  ) * 100

        return round(
            percent,
            2,
        )

    # ======================================================
    # POSITION SIZE
    # ======================================================

    def _position_size(
            self,
            confidence,
            rr,
    ):

        score = (
                        confidence
                        / 100
                ) * rr

        if score >= 2.5:
            return 1.0

        if score >= 2.0:
            return 0.75

        if score >= 1.5:
            return 0.50

        return 0.25

    # ======================================================
    # RISK SCORE
    # ======================================================

    def _risk_score(
            self,
            confidence,
            rr,
            volatility,
    ):

        score = 50

        score -= confidence * 0.35

        score -= rr * 8

        score += volatility * 4

        score = max(
            0,
            min(
                100,
                score,
            ),
        )

        return round(
            score,
            1,
        )

    # ======================================================
    # CURRENT PROFIT
    # ======================================================

    def current_profit(

            self,

            direction,

            entry,

            current_price,

    ):

        if direction == "BULLISH":
            return current_price - entry

        return entry - current_price

    # ======================================================
    # BREAKEVEN
    # ======================================================

    def should_move_breakeven(

            self,

            profit,

            risk,

    ):

        if risk <= 0:
            return False

        return (

                profit

                >=

                risk * self.breakeven_trigger

        )

    # ======================================================
    # PARTIAL EXIT
    # ======================================================

    def should_book_partial(

            self,

            profit,

            risk,

    ):

        if risk <= 0:
            return False

        return (

                profit

                >=

                risk * self.partial_trigger

        )

    # ======================================================
    # TRAILING STOP
    # ======================================================

    def trailing_stop(

            self,

            direction,

            current_price,

            atr,

    ):

        distance = (

                atr

                *

                self.trailing_multiplier

        )

        if direction == "BULLISH":
            return current_price - distance

        return current_price + distance

    # ======================================================
    # LIVE UPDATE
    # ======================================================

    def update_trade(

            self,

            assessment,

            direction,

            current_price,

            atr,

    ):

        profit = self.current_profit(

            direction,

            assessment.entry,

            current_price,

        )

        assessment.current_profit_points = round(

            profit,

            2,

        )

        risk = abs(

            assessment.entry

            -

            assessment.stop_loss

        )

        # ------------------------------

        # MOVE TO COST

        # ------------------------------

        if (

                not assessment.breakeven_active

                and

                self.should_move_breakeven(

                    profit,

                    risk,

                )

        ):
            assessment.current_stop = (

                assessment.entry

            )

            assessment.breakeven_active = True

            assessment.trade_status = "BREAKEVEN"

        # ------------------------------

        # PARTIAL

        # ------------------------------

        if (

                not assessment.booked_partial

                and

                self.should_book_partial(

                    profit,

                    risk,

                )

        ):
            assessment.booked_partial = True

            assessment.trade_status = "BOOK_PARTIAL"

        # ------------------------------

        # TRAIL

        # ------------------------------

        if assessment.booked_partial:
            assessment.trail_stop = (

                self.trailing_stop(

                    direction,

                    current_price,

                    atr,

                )

            )

            assessment.trade_status = "TRAILING"

        return assessment

    # ======================================================
    # STOP LOSS HIT
    # ======================================================

    def stop_hit(
            self,
            direction,
            current_price,
            stop,
    ):

        if direction == "BULLISH":
            return current_price <= stop

        return current_price >= stop

    # ======================================================
    # TARGET HIT
    # ======================================================

    def target_hit(
            self,
            direction,
            current_price,
            target,
    ):

        if direction == "BULLISH":
            return current_price >= target

        return current_price <= target

    # ======================================================
    # EMERGENCY EXIT
    # ======================================================

    def emergency_exit_required(
            self,
            confidence,
            emergency_signal=False,
    ):

        if emergency_signal:
            return True

        if confidence < 35:
            return True

        return False

    # ======================================================
    # MONITOR ACTIVE TRADE
    # ======================================================

    def monitor_trade(

            self,

            assessment,

            direction,

            current_price,

            confidence,

            atr,

            emergency_signal=False,

    ):

        assessment = self.update_trade(

            assessment,

            direction,

            current_price,

            atr,

        )

        # ---------------------------------
        # STOP LOSS
        # ---------------------------------

        stop = (

            assessment.trail_stop

            if assessment.trail_stop

            else

            assessment.current_stop

            if assessment.current_stop

            else

            assessment.stop_loss

        )

        if self.stop_hit(

                direction,

                current_price,

                stop,

        ):
            assessment.trade_completed = True

            assessment.stop_hit = True

            assessment.exit_reason = "STOP_LOSS"

            assessment.exit_price = current_price

            assessment.trade_status = "EXIT"

            return assessment

        # ---------------------------------
        # TARGET 1
        # ---------------------------------

        if (

                not assessment.target1_hit

                and

                self.target_hit(

                    direction,

                    current_price,

                    assessment.target1,

                )

        ):
            assessment.target1_hit = True

            assessment.trade_status = "TARGET1"

        # ---------------------------------
        # TARGET 2
        # ---------------------------------

        if (

                not assessment.target2_hit

                and

                self.target_hit(

                    direction,

                    current_price,

                    assessment.target2,

                )

        ):
            assessment.target2_hit = True

            assessment.trade_completed = True

            assessment.trade_status = "TARGET2"

            assessment.exit_reason = "TARGET_REACHED"

            assessment.exit_price = current_price

            return assessment

        # ---------------------------------
        # EMERGENCY EXIT
        # ---------------------------------

        if self.emergency_exit_required(

                confidence,

                emergency_signal,

        ):
            assessment.trade_completed = True

            assessment.emergency_exit = True

            assessment.trade_status = "EXIT"

            assessment.exit_reason = "EMERGENCY_EXIT"

            assessment.exit_price = current_price

            return assessment

        return assessment


# ==========================================================
# SINGLETON
# ==========================================================

risk_manager = RiskManager()