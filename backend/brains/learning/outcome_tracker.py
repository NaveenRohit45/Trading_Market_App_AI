"""
Learning Brain - Outcome Tracker

Author : Super Cat
Project : Trading Market AI

Responsibilities
----------------
✔ Record completed trades
✔ Calculate Profit/Loss
✔ Calculate Points
✔ Calculate Holding Time
✔ Track Win/Loss
✔ Provide Performance Statistics
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .models import PredictionRecord, TradeOutcome
from .storage import LearningStorage


class OutcomeTracker:

    def __init__(self, storage: LearningStorage | None = None):

        self.storage = storage or LearningStorage()

    # ==========================================================
    # Calculate Profit Points
    # ==========================================================

    @staticmethod
    def calculate_points(
        decision: str,
        entry_price: float,
        exit_price: float,
    ) -> float:

        decision = decision.upper()

        if decision == "BUY":
            return round(exit_price - entry_price, 2)

        elif decision == "SELL":
            return round(entry_price - exit_price, 2)

        return 0.0

    # ==========================================================
    # Calculate PnL
    # ==========================================================

    @staticmethod
    def calculate_pnl(
        points: float,
        quantity: int,
    ) -> float:

        return round(points * quantity, 2)

    # ==========================================================
    # Holding Time
    # ==========================================================

    @staticmethod
    def calculate_holding_minutes(
        entry_time: datetime,
        exit_time: datetime,
    ) -> float:

        seconds = (exit_time - entry_time).total_seconds()

        return round(seconds / 60.0, 2)

    # ==========================================================
    # Record Outcome
    # ==========================================================

    def record_outcome(

        self,

        prediction: PredictionRecord,

        exit_price: float,

        quantity: int = 1,

        exit_reason: str = "Target Hit",

        exit_time: Optional[datetime] = None,

    ) -> TradeOutcome:

        if exit_time is None:
            exit_time = datetime.now()

        points = self.calculate_points(
            prediction.decision,
            prediction.current_price,
            exit_price,
        )

        pnl = self.calculate_pnl(
            points,
            quantity,
        )

        holding = self.calculate_holding_minutes(
            prediction.timestamp,
            exit_time,
        )

        success = points > 0

        outcome = TradeOutcome(

            prediction_id=prediction.prediction_id,

            entry_price=prediction.current_price,

            exit_price=exit_price,

            quantity=quantity,

            holding_minutes=holding,

            exit_reason=exit_reason,

            profit_points=points,

            pnl=pnl,

            success=success,

            timestamp=exit_time,
        )

        self.storage.save_trade_outcome(outcome)

        return outcome

    # ==========================================================
    # Retrieve Outcome
    # ==========================================================

    def get_outcome(
        self,
        prediction_id: str,
    ):

        return self.storage.get_trade_outcome(prediction_id)

    # ==========================================================
    # All Outcomes
    # ==========================================================

    def all_outcomes(self):

        return self.storage.get_all_trade_outcomes()

    # ==========================================================
    # Win Count
    # ==========================================================

    def win_count(self):

        outcomes = self.storage.get_all_trade_outcomes()

        return sum(
            1
            for row in outcomes
            if row["success"] == 1
        )

    # ==========================================================
    # Loss Count
    # ==========================================================

    def loss_count(self):

        outcomes = self.storage.get_all_trade_outcomes()

        return sum(
            1
            for row in outcomes
            if row["success"] == 0
        )

    # ==========================================================
    # Win Rate
    # ==========================================================

    def win_rate(self):

        total = self.storage.outcome_count()

        if total == 0:
            return 0.0

        wins = self.win_count()

        return round((wins / total) * 100, 2)

    # ==========================================================
    # Total Profit
    # ==========================================================

    def total_profit(self):

        outcomes = self.storage.get_all_trade_outcomes()

        return round(

            sum(row["pnl"] for row in outcomes),

            2,

        )

    # ==========================================================
    # Average Profit
    # ==========================================================

    def average_profit(self):

        outcomes = self.storage.get_all_trade_outcomes()

        if not outcomes:
            return 0.0

        return round(

            sum(row["pnl"] for row in outcomes) / len(outcomes),

            2,

        )

    # ==========================================================
    # Best Trade
    # ==========================================================

    def best_trade(self):

        outcomes = self.storage.get_all_trade_outcomes()

        if not outcomes:
            return None

        return max(
            outcomes,
            key=lambda x: x["pnl"],
        )

    # ==========================================================
    # Worst Trade
    # ==========================================================

    def worst_trade(self):

        outcomes = self.storage.get_all_trade_outcomes()

        if not outcomes:
            return None

        return min(
            outcomes,
            key=lambda x: x["pnl"],
        )

    # ==========================================================
    # Dashboard Summary
    # ==========================================================

    def summary(self):

        return {

            "total_trades": self.storage.outcome_count(),

            "wins": self.win_count(),

            "losses": self.loss_count(),

            "win_rate": self.win_rate(),

            "total_profit": self.total_profit(),

            "average_profit": self.average_profit(),

        }