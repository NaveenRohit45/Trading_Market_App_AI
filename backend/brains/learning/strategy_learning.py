"""
Trading Market AI V2

Strategy Learning

Author : Super Cat

Learns from completed trades and continuously
improves every AI brain.
"""

from __future__ import annotations
from datetime import datetime

from .models import (
    PredictionRecord,
    TradeOutcome,
    StrategyRecommendation,
)

from .storage import LearningStorage

from .confidence_optimizer import ConfidenceOptimizer
from .market_regime import MarketRegimeAnalyzer

class StrategyLearning:
    """
    Learns from historical trade outcomes.
    """

    def __init__(
        self,
        storage: LearningStorage | None = None,
        optimizer: ConfidenceOptimizer | None = None,
    ):

        self.storage = storage or LearningStorage()

        self.optimizer = optimizer or ConfidenceOptimizer()

        self.regime = MarketRegimeAnalyzer()

        self.total_trades = 0

        self.total_wins = 0

        self.total_losses = 0

        # ---------------------------------------------
        # Brain Statistics
        # ---------------------------------------------

        self.brains = {

            "price_action": self._new_brain(),

            "live_market": self._new_brain(),

            "options": self._new_brain(),

            "global_market": self._new_brain(),

        }

        # ---------------------------------------------
        # Strategy Database
        # ---------------------------------------------

        self.strategies = {}
        # ---------------------------------------------
        # Strategy Ranking
        # ---------------------------------------------

        self.strategy_ranking = {}



    # =====================================================
    # Rank Strategies
    # =====================================================

    def rank_strategies(self):

        self.strategy_ranking.clear()

        for key, strategy in self.strategies.items():
            score = self._strategy_score(strategy)

            self.strategy_ranking[key] = score

    # =====================================================
    # Strategy Score
    # =====================================================

    def _strategy_score(
            self,
            strategy: dict,
    ) -> float:

        accuracy = strategy["accuracy"]

        occurrences = strategy["total"]

        average_profit = strategy["average_profit"]

        score = (

                accuracy * 0.50 +

                min(occurrences, 100) * 0.20 +

                average_profit * 0.30

        )

        return round(score, 2)

    # =====================================================
    # Learn
    # =====================================================

    def learn(
            self,
            prediction: PredictionRecord,
            outcome: TradeOutcome,
    ):

        self.total_trades += 1

        if outcome.success:
            self.total_wins += 1
        else:
            self.total_losses += 1

        # Update every brain

        self._update_brains(
            prediction,
            outcome,
        )

        # Learn strategy

        self._learn_strategy(
            prediction,
            outcome,
        )

        self.rank_strategies()

    # =====================================================
    # Strategy Recommendation
    # =====================================================

    def recommend(
            self,
            prediction: PredictionRecord,
    ) -> StrategyRecommendation:

        key = self._strategy_key(prediction)

        strategy = self.strategies.get(key)

        # ---------------------------------------------
        # Extract normalized market features
        # ---------------------------------------------

        features = self.regime.extract(
            prediction
        )

        # -------------------------------------------------
        # Unknown Strategy
        # -------------------------------------------------

        if strategy is None:
            return StrategyRecommendation(

                recommendation=prediction.decision,

                confidence=50.0,

                risk_multiplier=self._risk_multiplier(strategy),

                position_multiplier=self._position_multiplier(strategy),

                stop_loss_multiplier=1.0,

                take_profit_multiplier=1.0,

                reasoning=[

                    "No historical strategy found."

                ],

            )

        confidence = self._strategy_confidence(strategy)

        agreement, agreement_reason = self._brain_agreement(
            prediction
        )

        # ---------------------------------------------
        # Adjust confidence using brain agreement
        # ---------------------------------------------

        if agreement >= 100:

            confidence += 5

        elif agreement >= 75:

            confidence += 2

        elif agreement >= 50:

            confidence -= 5

        else:

            confidence -= 10

        confidence = max(
            0,
            min(confidence, 100),
        )


        recommendation = StrategyRecommendation(

            recommendation=prediction.decision,

            confidence=confidence,

            risk_multiplier=self._risk_multiplier(strategy),

            position_multiplier=self._position_multiplier(strategy),

            stop_loss_multiplier=1.0,

            take_profit_multiplier=1.0,

            reasoning=[

                f"Historical Accuracy : {strategy['accuracy']}%",

                f"Trades : {strategy['total']}",

                f"Average Profit : {strategy['average_profit']}",

                f"Brain Agreement : {agreement}%",

                f"Market Session : {features.market_session}",

                f"ATR Bucket : {features.atr_bucket}",

                f"VIX Bucket : {features.vix_bucket}",

                *agreement_reason,

            ],

        )

        return recommendation

    # =====================================================
    # Best Strategies
    # =====================================================

    def best_strategies(
            self,
            limit: int = 10,
    ):

        ranked = sorted(

            self.strategy_ranking.items(),

            key=lambda x: x[1],

            reverse=True,

        )

        return ranked[:limit]

    # =====================================================
    # Worst Strategies
    # =====================================================

    def worst_strategies(
            self,
            limit: int = 10,
    ):

        ranked = sorted(

            self.strategy_ranking.items(),

            key=lambda x: x[1]

        )

        return ranked[:limit]


    # =====================================================
    # Update Brains
    # =====================================================

    def _update_brains(

            self,

            prediction: PredictionRecord,

            outcome: TradeOutcome,

    ):

        signals = {

            "price_action":

                prediction.price_action_signal,

            "live_market":

                prediction.live_market_signal,

            "options":

                prediction.options_signal,

            "global_market":

                prediction.global_market_signal,

        }

        for brain_name, signal in signals.items():

            stats = self.brains[brain_name]

            stats["total"] += 1

            if signal == prediction.decision:

                if outcome.success:

                    stats["wins"] += 1

                else:

                    stats["losses"] += 1

            stats["accuracy"] = round(

                stats["wins"]

                /

                max(1, stats["total"])

                * 100,

                2,

            )

            self.optimizer.update_brain_accuracy(

                brain_name,

                stats["accuracy"],

                stats["total"],

                stats["wins"],

            )

    # =====================================================
    # Learn Strategy
    # =====================================================

    def _learn_strategy(
            self,
            prediction: PredictionRecord,
            outcome: TradeOutcome,
    ):

        key = self._strategy_key(
            prediction
        )

        strategy = self.strategies.setdefault(

            key,

            self._new_strategy(),

        )

        strategy["total"] += 1

        if outcome.success:

            strategy["wins"] += 1

            strategy["profit_sum"] += outcome.pnl

        else:

            strategy["losses"] += 1

            strategy["loss_sum"] += abs(outcome.pnl)

        strategy["accuracy"] = round(

            strategy["wins"]

            /

            strategy["total"]

            * 100,

            2,

        )

        if strategy["wins"]:
            strategy["average_profit"] = round(

                strategy["profit_sum"]

                /

                strategy["wins"],

                2,

            )

        if strategy["losses"]:
            strategy["average_loss"] = round(

                strategy["loss_sum"]

                /

                strategy["losses"],

                2,

            )

        strategy["last_updated"] = datetime.now()

        strategy["best_profit"] = max(
            strategy["best_profit"],
            outcome.pnl,
        )

        strategy["worst_loss"] = min(
            strategy["worst_loss"],
            outcome.pnl,
        )

    # =====================================================
    # Market Regime
    # =====================================================

    def _market_regime(
            self,
            prediction: PredictionRecord,
    ) -> str:
        """
        Build a market regime string used for
        strategy learning.
        """

        parts = [

            prediction.market_session,

            prediction.trend,

            prediction.atr_bucket,

            prediction.vix_bucket,

        ]

        return "|".join(parts)

    # =====================================================
    # Strategy Key
    # =====================================================

    def _strategy_key(
        self,
        prediction: PredictionRecord,
    ) -> str:

        regime = self._market_regime(prediction)

        return "|".join([

            prediction.timeframe,

            regime,

            prediction.price_action_signal,

            prediction.live_market_signal,

            prediction.options_signal,

            prediction.global_market_signal,

            prediction.decision,

        ])

    # =====================================================
    # Risk Multiplier
    # =====================================================

    def _risk_multiplier(
            self,
            strategy: dict,
    ) -> float:
        """
        Calculate risk multiplier based on
        historical strategy performance.
        """

        accuracy = strategy["accuracy"]

        trades = strategy["total"]

        # Very small sample size
        if trades < 10:
            return 0.75

        if accuracy >= 90:
            return 1.50

        if accuracy >= 80:
            return 1.30

        if accuracy >= 70:
            return 1.15

        if accuracy >= 60:
            return 1.00

        if accuracy >= 50:
            return 0.80

        return 0.60

    # =====================================================
    # Position Multiplier
    # =====================================================

    def _position_multiplier(
            self,
            strategy: dict,
    ) -> float:
        """
        Calculate position size multiplier based on
        historical strategy quality.

        Returns
        -------
        Position size multiplier
        """

        accuracy = strategy["accuracy"]
        trades = strategy["total"]
        avg_profit = strategy["average_profit"]
        avg_loss = strategy["average_loss"]

        # ---------------------------------------------
        # Small sample protection
        # ---------------------------------------------

        if trades < 10:
            return 0.50

        score = 0.0

        # ---------------------------------------------
        # Accuracy (50 points)
        # ---------------------------------------------

        score += min(accuracy, 100) * 0.50

        # ---------------------------------------------
        # Experience (20 points)
        # ---------------------------------------------

        score += min(trades, 100) * 0.20

        # ---------------------------------------------
        # Profitability (20 points)
        # ---------------------------------------------

        profit_score = min(avg_profit, 300) / 300

        score += profit_score * 20

        # ---------------------------------------------
        # Loss Control (10 points)
        # Smaller losses = higher score
        # ---------------------------------------------

        if avg_loss > 0:
            loss_score = max(0, 1 - (avg_loss / 300))

            score += loss_score * 10

        # ---------------------------------------------
        # Final Multiplier
        # ---------------------------------------------

        if score >= 90:
            return 1.50

        if score >= 80:
            return 1.30

        if score >= 70:
            return 1.15

        if score >= 60:
            return 1.00

        if score >= 50:
            return 0.80

        return 0.60

    # =====================================================
    # Strategy Confidence
    # =====================================================

    def _strategy_confidence(
            self,
            strategy: dict,
    ) -> float:
        """
        Calculate overall confidence for a strategy.

        Returns
        -------
        Confidence (0-100)
        """

        accuracy = strategy["accuracy"]
        trades = strategy["total"]
        avg_profit = strategy["average_profit"]
        avg_loss = strategy["average_loss"]

        risk = self._risk_multiplier(strategy)

        position = self._position_multiplier(strategy)

        confidence = 0.0

        # ---------------------------------------------
        # Historical Accuracy (35%)
        # ---------------------------------------------

        confidence += min(accuracy, 100) * 0.35

        # ---------------------------------------------
        # Experience (20%)
        # ---------------------------------------------

        confidence += (min(trades, 200) / 200) * 20

        # ---------------------------------------------
        # Average Profit (15%)
        # ---------------------------------------------

        confidence += (

                              min(avg_profit, 300)

                              / 300

                      ) * 15

        # ---------------------------------------------
        # Average Loss Control (10%)
        # Smaller losses = better confidence
        # ---------------------------------------------

        if avg_loss > 0:

            confidence += (

                              max(

                                  0,

                                  1 - (avg_loss / 300)

                              )

                          ) * 10

        else:

            confidence += 10

        # ---------------------------------------------
        # Risk Quality (10%)
        # ---------------------------------------------

        confidence += (

                              risk

                              / 1.5

                      ) * 10

        # ---------------------------------------------
        # Position Quality (10%)
        # ---------------------------------------------

        confidence += (

                              position

                              / 1.5

                      ) * 10

        return round(

            min(confidence, 100),

            2,

        )

    # =====================================================
    # Brain Agreement
    # =====================================================

    def _brain_agreement(
            self,
            prediction: PredictionRecord,
    ) -> tuple[float, list[str]]:
        """
        Measure agreement between all AI brains.

        Returns
        -------
        (agreement %, reasoning)
        """

        signals = [

            prediction.price_action_signal,

            prediction.live_market_signal,

            prediction.options_signal,

            prediction.global_market_signal,

        ]

        decision = prediction.decision

        agreement = sum(

            signal == decision

            for signal in signals

        )

        percentage = round(

            agreement / len(signals) * 100,

            2,

        )

        reasons = []

        if agreement == 4:

            reasons.append(

                "All AI brains agree."

            )

        elif agreement == 3:

            reasons.append(

                "Strong agreement between AI brains."

            )

        elif agreement == 2:

            reasons.append(

                "Mixed signals detected."

            )

        else:

            reasons.append(

                "Low agreement between AI brains."

            )

        return percentage, reasons

    # =====================================================
    # New Strategy
    # =====================================================

    @staticmethod
    def _new_strategy():

        return {

            "total": 0,

            "wins": 0,

            "losses": 0,

            "accuracy": 0.0,

            "average_profit": 0.0,

            "average_loss": 0.0,

            "profit_sum": 0.0,

            "loss_sum": 0.0,

            "last_updated": None,

            "best_profit": 0.0,

            "worst_loss": 0.0,

            "average_holding_time": 0.0,

        }

    # =====================================================
    # New Brain
    # =====================================================

    @staticmethod
    def _new_brain():

        return {

            "total": 0,

            "wins": 0,

            "losses": 0,

            "accuracy": 0.0,

        }