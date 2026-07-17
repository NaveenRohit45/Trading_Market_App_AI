"""
Trading Market AI V2

Confidence Optimizer

Author : Super Cat

Responsibilities
----------------
✔ Optimize AI confidence
✔ Apply Learning Brain bonus
✔ Apply Brain Agreement bonus
✔ Apply Volatility penalty
✔ Apply Risk penalty
✔ Return explainable confidence
"""

from __future__ import annotations

from .models import (
    PredictionRecord,
    PatternAnalysis,
    OptimizedConfidence,
)


class ConfidenceOptimizer:
    """
    Optimizes confidence produced by all AI brains.
    """

    # --------------------------------------------------

    def __init__(self):

        # ---------------------------------------------
        # Confidence Limits
        # ---------------------------------------------

        self.minimum_confidence = 5.0

        self.maximum_confidence = 99.0

        # ---------------------------------------------
        # Weights
        # ---------------------------------------------

        self.pattern_weight = 1.0

        self.agreement_weight = 1.0

        self.risk_weight = 1.0

        self.volatility_weight = 1.0

        # ---------------------------------------------
        # Agreement Bonus
        # ---------------------------------------------

        self.agreement_bonus = {

            4: 8.0,

            3: 5.0,

            2: 2.0,

            1: 0.0,

            0: 0.0,

        }

        # ---------------------------------------------
        # VIX Penalty
        # ---------------------------------------------

        self.vix_penalties = {

            25: 10.0,

            20: 6.0,

            15: 3.0,

        }

        # ---------------------------------------------
        # Risk Penalty
        # ---------------------------------------------

        self.high_risk_penalty = 6.0

        self.medium_risk_penalty = 3.0

        # ---------------------------------------------
        # Brain Accuracy Bonus
        # ---------------------------------------------

        # ---------------------------------------------
        # Brain Statistics
        # ---------------------------------------------

        self.brain_statistics = {

            "price_action": {

                "accuracy": 0.0,
                "bonus": 0.0,
                "total_predictions": 0,
                "correct_predictions": 0,

            },

            "live_market": {

                "accuracy": 0.0,
                "bonus": 0.0,
                "total_predictions": 0,
                "correct_predictions": 0,

            },

            "options": {

                "accuracy": 0.0,
                "bonus": 0.0,
                "total_predictions": 0,
                "correct_predictions": 0,

            },

            "global_market": {

                "accuracy": 0.0,
                "bonus": 0.0,
                "total_predictions": 0,
                "correct_predictions": 0,

            }

        }

    # ==================================================
    # Main API
    # ==================================================

    def optimize(

        self,

        prediction: PredictionRecord,

        analysis: PatternAnalysis,

    ) -> OptimizedConfidence:

        confidence = prediction.confidence

        adjustments = []

        # Pattern bonus

        confidence, pattern_bonus, adjustment = self._pattern_bonus(
            confidence,
            analysis,
        )
        adjustments.append(adjustment)

        confidence, historical_bonus, adjustment = self._historical_accuracy_bonus(
            confidence,
            prediction,
        )
        adjustments.append(adjustment)

        # Brain agreement

        confidence, agreement_bonus, adjustment = self._brain_agreement_bonus(
            confidence,
            prediction,
        )
        adjustments.append(adjustment)

        # Volatility

        confidence, volatility_penalty, adjustment = self._volatility_penalty(
            confidence,
            prediction,
        )
        adjustments.append(adjustment)

        # Risk

        confidence, risk_penalty, adjustment = self._risk_penalty(
            confidence,
            prediction,
        )
        adjustments.append(adjustment)

        confidence = max(

            self.minimum_confidence,

            min(

                confidence,

                self.maximum_confidence,

            ),

        )

        return OptimizedConfidence(

            base_confidence=prediction.confidence,

            final_confidence=round(confidence, 2),

            pattern_bonus=pattern_bonus,

            agreement_bonus=agreement_bonus,

            volatility_penalty=volatility_penalty,

            historical_bonus=historical_bonus,

            risk_penalty=risk_penalty,

            adjustments=adjustments,

        )

    # ==================================================
    # Pattern Bonus
    # ==================================================

    def _pattern_bonus(
        self,
        confidence: float,
        analysis: PatternAnalysis,
    ) -> tuple[float, float, str]:

        bonus = analysis.confidence_bonus * self.pattern_weight

        confidence += bonus

        return (

            confidence,

            bonus,

            f"Pattern Memory: +{bonus:.2f}"

        )

    # ==================================================
    # Brain Agreement
    # ==================================================

    def _brain_agreement_bonus(

            self,

            confidence,

            prediction,

    ):

        signals = [

            prediction.price_action_signal,

            prediction.live_market_signal,

            prediction.options_signal,

            prediction.global_market_signal,

        ]

        agreement = sum(

            1

            for signal in signals

            if signal == prediction.decision

        )

        bonus = self.agreement_bonus.get(

            agreement,

            0.0,

        )

        confidence += bonus

        return (

            confidence,

            bonus,

            f"Brain Agreement ({agreement}/4): +{bonus:.2f}"

        )

    # ==================================================
    # Volatility
    # ==================================================

    def _volatility_penalty(

            self,

            confidence,

            prediction,

    ):

        penalty = 0.0

        for level, value in sorted(

                self.vix_penalties.items(),

                reverse=True,

        ):

            if prediction.vix >= level:
                penalty = value

                break

        confidence -= penalty

        return (

            confidence,

            penalty,

            f"Volatility Penalty: -{penalty:.2f}"

        )

    # ==================================================
    # Risk Penalty
    # ==================================================

    def _risk_penalty(

            self,

            confidence,

            prediction,

    ):

        penalty = 0.0

        stop_distance = abs(

            prediction.current_price -

            prediction.support

        )

        if stop_distance > prediction.atr * 2:

            penalty = self.high_risk_penalty

        elif stop_distance > prediction.atr:

            penalty = self.medium_risk_penalty

        confidence -= penalty

        return (

            confidence,

            penalty,

            f"Risk Penalty: -{penalty:.2f}"

        )

    # ==================================================
    # Historical Accuracy
    # ==================================================

    def _historical_accuracy_bonus(
        self,
        confidence: float,
        prediction: PredictionRecord,
    ) -> tuple[float, float, str]:

        bonus = 0.0

        if prediction.price_action_signal == prediction.decision:

            bonus += self.brain_statistics["price_action"]["bonus"]

        if prediction.live_market_signal == prediction.decision:

            bonus += self.brain_statistics["live_market"]["bonus"]

        if prediction.options_signal == prediction.decision:

            bonus += self.brain_statistics["options"]["bonus"]

        if prediction.global_market_signal == prediction.decision:

            bonus += self.brain_statistics["global_market"]["bonus"]

        confidence += bonus

        return (

            confidence,

            bonus,

            f"Historical Brain Bonus: +{bonus:.2f}"

        )

    # ==================================================
    # Update Brain Accuracy
    # ==================================================

    def update_brain_accuracy(
            self,
            brain_name: str,
            accuracy: float,
            total_predictions: int,
            correct_predictions: int,
    ):

        if accuracy >= 90:
            bonus = 6.0

        elif accuracy >= 80:
            bonus = 4.0

        elif accuracy >= 70:
            bonus = 2.0

        else:
            bonus = 0.0

        self.brain_statistics[brain_name] = {

            "accuracy": accuracy,

            "bonus": bonus,

            "total_predictions": total_predictions,

            "correct_predictions": correct_predictions,

        }