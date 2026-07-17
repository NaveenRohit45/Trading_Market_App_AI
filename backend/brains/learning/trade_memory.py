"""
Learning Brain - Trade Memory

Author : Super Cat
Project : Trading Market AI

Responsibilities
----------------
✔ Record every AI prediction
✔ Retrieve prediction history
✔ Search previous trades
✔ Query statistics

This module never talks to SQLite directly.
It always uses LearningStorage.
"""

from __future__ import annotations

from typing import List, Optional

from .models import PredictionRecord
from .storage import LearningStorage


class TradeMemory:

    def __init__(self, storage: LearningStorage | None = None):

        self.storage = storage or LearningStorage()

    # ==========================================================
    # Record Prediction
    # ==========================================================

    def record_prediction(
        self,
        prediction: PredictionRecord,
    ) -> str:

        """
        Save prediction into database.

        Returns
        -------
        prediction_id
        """

        self.storage.save_prediction(prediction)

        return prediction.prediction_id

    # ==========================================================
    # Get Prediction
    # ==========================================================

    def get_prediction(
        self,
        prediction_id: str,
    ):

        return self.storage.get_prediction(prediction_id)

    # ==========================================================
    # Recent Predictions
    # ==========================================================

    def recent_predictions(
        self,
        limit: int = 20,
    ):

        return self.storage.get_recent_predictions(limit)

    # ==========================================================
    # All Predictions
    # ==========================================================

    def all_predictions(self):

        return self.storage.get_all_predictions()

    # ==========================================================
    # Prediction Count
    # ==========================================================

    def prediction_count(self):

        return self.storage.prediction_count()

    # ==========================================================
    # Delete Prediction
    # ==========================================================

    def delete_prediction(
        self,
        prediction_id: str,
    ):

        self.storage.delete_prediction(prediction_id)

    # ==========================================================
    # Search By Symbol
    # ==========================================================

    def predictions_by_symbol(
        self,
        symbol: str,
    ):

        predictions = self.storage.get_all_predictions()

        return [

            row

            for row in predictions

            if row["symbol"] == symbol

        ]

    # ==========================================================
    # Search By Decision
    # ==========================================================

    def predictions_by_decision(
        self,
        decision: str,
    ):

        predictions = self.storage.get_all_predictions()

        return [

            row

            for row in predictions

            if row["decision"] == decision

        ]

    # ==========================================================
    # High Confidence Trades
    # ==========================================================

    def high_confidence_predictions(
        self,
        minimum: float = 80.0,
    ):

        predictions = self.storage.get_all_predictions()

        return [

            row

            for row in predictions

            if row["confidence"] >= minimum

        ]

    # ==========================================================
    # Clear Database
    # ==========================================================

    def clear(self):

        predictions = self.storage.get_all_predictions()

        for row in predictions:

            self.storage.delete_prediction(
                row["prediction_id"]
            )

    # ==========================================================
    # Summary
    # ==========================================================

    def summary(self):

        predictions = self.storage.get_all_predictions()

        buy = 0
        sell = 0
        hold = 0

        for row in predictions:

            decision = row["decision"]

            if decision == "BUY":
                buy += 1

            elif decision == "SELL":
                sell += 1

            else:
                hold += 1

        return {

            "total": len(predictions),

            "buy": buy,

            "sell": sell,

            "hold": hold,

        }