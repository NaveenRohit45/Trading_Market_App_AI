"""
Learning Brain

Author : Super Cat
Project : Trading Market AI

Main orchestrator for the Learning Brain.

All other modules should communicate ONLY with this class.

Architecture

Trade Decision Engine
        │
        ▼
LearningBrain
        │
 ┌──────┼──────────┐
 ▼      ▼          ▼
TradeMemory
OutcomeTracker
Storage

Future

PatternMemory
ConfidenceOptimizer
StrategyLearning
MistakeAnalyzer
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime

from .models import (
    PredictionRecord,
    TradeOutcome,
    LearningResult,
)

from .storage import LearningStorage
from .trade_memory import TradeMemory
from .outcome_tracker import OutcomeTracker


class LearningBrain:

    def __init__(self):

        self.storage = LearningStorage()

        self.trade_memory = TradeMemory(self.storage)

        self.outcome_tracker = OutcomeTracker(self.storage)

    # =====================================================
    # Record Prediction
    # =====================================================

    def record_prediction(
        self,
        prediction: PredictionRecord,
    ) -> str:

        """
        Save AI prediction.

        Returns
        -------
        prediction_id
        """

        return self.trade_memory.record_prediction(
            prediction
        )

    # =====================================================
    # Record Trade Outcome
    # =====================================================

    def record_outcome(

        self,

        prediction: PredictionRecord,

        exit_price: float,

        quantity: int = 1,

        exit_reason: str = "Manual",

        exit_time: Optional[datetime] = None,

    ) -> TradeOutcome:

        return self.outcome_tracker.record_outcome(

            prediction=prediction,

            exit_price=exit_price,

            quantity=quantity,

            exit_reason=exit_reason,

            exit_time=exit_time,

        )

    # =====================================================
    # Retrieve Prediction
    # =====================================================

    def get_prediction(
        self,
        prediction_id: str,
    ):

        return self.trade_memory.get_prediction(
            prediction_id
        )

    # =====================================================
    # Retrieve Outcome
    # =====================================================

    def get_outcome(
        self,
        prediction_id: str,
    ):

        return self.outcome_tracker.get_outcome(
            prediction_id
        )

    # =====================================================
    # Recent Predictions
    # =====================================================

    def recent_predictions(
        self,
        limit: int = 20,
    ):

        return self.trade_memory.recent_predictions(limit)

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self):

        return {

            "predictions": self.trade_memory.prediction_count(),

            "completed_trades": self.storage.outcome_count(),

            "wins": self.outcome_tracker.win_count(),

            "losses": self.outcome_tracker.loss_count(),

            "win_rate": self.outcome_tracker.win_rate(),

            "total_profit": self.outcome_tracker.total_profit(),

            "average_profit": self.outcome_tracker.average_profit(),

        }

    # =====================================================
    # Dashboard Summary
    # =====================================================

    def dashboard(self):

        return {

            "memory": self.trade_memory.summary(),

            "performance": self.outcome_tracker.summary(),

        }

    # =====================================================
    # Analyze Historical Learning
    # =====================================================

    def analyze(
        self,
        prediction: PredictionRecord,
    ) -> LearningResult:

        """
        Phase 1

        Currently returns original confidence.

        Future versions will:

        - Search similar setups
        - Pattern matching
        - Historical win rate
        - Adaptive confidence
        - Mistake analysis
        """

        return LearningResult(

            historical_matches=0,

            historical_win_rate=0.0,

            adjusted_confidence=prediction.confidence,

            recommendation=prediction.decision,

            notes=[

                "Learning Phase 1",

                "Historical learning not enabled.",

            ],

        )

    # =====================================================
    # Reset Database
    # =====================================================

    def clear_learning_data(self):

        predictions = self.trade_memory.all_predictions()

        for row in predictions:

            self.trade_memory.delete_prediction(
                row["prediction_id"]
            )

        outcomes = self.outcome_tracker.all_outcomes()

        for row in outcomes:

            self.storage.delete_trade_outcome(
                row["prediction_id"]
            )

    # =====================================================
    # Health Check
    # =====================================================

    def health(self):

        return {

            "status": "healthy",

            "database": self.storage.db_path,

            "predictions": self.trade_memory.prediction_count(),

            "outcomes": self.storage.outcome_count(),

        }