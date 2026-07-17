"""
Trading Market AI V2
Pattern Memory

Production skeleton implementation.

This module orchestrates:
- Feature extraction
- Fingerprint generation
- Similarity search
- Historical statistics
"""

from __future__ import annotations

from statistics import mean
from collections import defaultdict

from .feature_extractor import FeatureExtractor
from .fingerprint import FingerprintGenerator
from .similarity_engine import SimilarityEngine
from .models import (
    PredictionRecord,
    PatternAnalysis,
    LearnedPattern,
)
from .storage import LearningStorage


class PatternMemory:

    def __init__(self, storage: LearningStorage | None = None):

        self.storage = storage or LearningStorage()
        self.extractor = FeatureExtractor()
        self.fingerprint = FingerprintGenerator()
        self.similarity = SimilarityEngine()

        # -------------------------------------------------
        # Pattern Index
        # -------------------------------------------------

        self.pattern_index = defaultdict(list)

        self.index_loaded = False

        # -------------------------------------------------
        # Pattern Cache
        # -------------------------------------------------

        self.pattern_cache = {}

        self.cache_hits = 0

        self.cache_misses = 0

        # -------------------------------------------------
        # Pattern Knowledge Base
        # -------------------------------------------------

        self.knowledge_base = {}

        self.learning_enabled = True

        self.load_knowledge_base()

    def analyze(self, prediction: PredictionRecord) -> PatternAnalysis:
        current_features = self.extractor.extract(prediction)
        self._load_pattern_index()
        fingerprint = self.fingerprint.generate(current_features)
        cached = self._cache_lookup(
            fingerprint
        )

        if cached is not None:

            return cached

        signature = self._build_signature(
            current_features
        )

        history = self.pattern_index.get(
            signature,
            []
        )

        if not history:
            return PatternAnalysis(
                pattern_key=fingerprint,
                fingerprint=fingerprint,
                notes=["No historical data available."]
            )

        return self._analyze_history(
            current_features,
            fingerprint,
            history,
        )

    def _analyze_history(
        self,
        current_features,
        fingerprint: str,
        history,
    ) -> PatternAnalysis:

        matches = []

        for historical in history:

            historical_features = self.extractor.extract(historical)

            similarity = self.similarity.compare(
                current_features,
                historical_features,
            )

            if similarity.score >= 75:
                outcome = self.storage.get_trade_outcome(
                    historical.prediction_id
                )

                if outcome is not None:
                    matches.append(
                        (
                            historical,
                            outcome,
                            similarity,
                        )
                    )

        if not matches:
            return PatternAnalysis(
                pattern_key=fingerprint,
                fingerprint=fingerprint,
                notes=["No similar historical patterns found."]
            )
        matches = self._rank_matches(
            # Keep only the best matches

            matches=matches[:25]
        )
        analysis = self._build_analysis(
            fingerprint,
            matches,
        )

        self._cache_save(
            fingerprint,
            analysis,
        )

        return analysis

    # =====================================================
    # Rank Matches
    # =====================================================

    def _rank_matches(
        self,
        matches,
    ):
        """
        Rank historical matches by quality.
        """

        def score(item):
            prediction, outcome, similarity = item

            return self._pattern_quality(

                similarity=similarity,

                outcome=outcome,

                total_matches=len(matches),

            )


        matches.sort(

            key=score,

            reverse=True,

        )

        return matches

    # =====================================================
    # Pattern Quality
    # =====================================================

    def _pattern_quality(
            self,
            similarity,
            outcome,
            total_matches: int,
    ) -> float:
        """
        Calculate an overall quality score for a
        historical pattern.

        Returns
        -------
        0 - 100
        """

        quality = 0.0

        # ---------------------------------------------
        # Similarity (40%)
        # ---------------------------------------------

        quality += similarity.score * 0.40

        # ---------------------------------------------
        # Win/Loss Result (30%)
        # ---------------------------------------------

        if outcome.success:
            quality += 30.0

        # ---------------------------------------------
        # Profit (15%)
        # ---------------------------------------------

        profit_score = min(
            max(outcome.pnl, 0),
            300,
        )

        quality += (profit_score / 300) * 15

        # ---------------------------------------------
        # Pattern Frequency (10%)
        # ---------------------------------------------

        frequency = min(
            total_matches,
            100,
        )

        quality += (frequency / 100) * 10

        # ---------------------------------------------
        # Recency (5%)
        # ---------------------------------------------

        quality += 5.0

        return round(
            quality,
            2,
        )

    # =====================================================
    # Pattern Confidence
    # =====================================================

    def _pattern_confidence(
            self,
            matches: int,
            win_rate: float,
            average_similarity: float,
            average_profit: float,
            age_score: float = 100.0,
    ) -> float:
        """
        Calculate confidence for a learned pattern.

        Returns
        -------
        0 - 100
        """

        confidence = 0.0

        # -----------------------------------------
        # Historical Sample Size (25%)
        # -----------------------------------------

        confidence += (

                              min(matches, 200)

                              / 200

                      ) * 25

        # -----------------------------------------
        # Win Rate (35%)
        # -----------------------------------------

        confidence += (

                              win_rate

                              / 100

                      ) * 35

        # -----------------------------------------
        # Similarity (25%)
        # -----------------------------------------

        confidence += (

                              average_similarity

                              / 100

                      ) * 25

        # -----------------------------------------
        # Profitability (10%)
        # -----------------------------------------

        confidence += (

                              min(

                                  max(average_profit, 0),

                                  300,

                              )

                              / 300

                      ) * 10

        # -----------------------------------------
        # Pattern Freshness (5%)
        # -----------------------------------------

        confidence += (

                              age_score

                              / 100

                      ) * 5

        return round(

            confidence,

            2,

        )

    def _build_analysis(
        self,
        fingerprint: str,
        matches,
    ) -> PatternAnalysis:

        wins = sum(
            1 for _, outcome, _ in matches
            if outcome.success
        )

        losses = len(matches) - wins

        profits = [
            outcome.pnl
            for _, outcome, _ in matches
            if outcome.pnl > 0
        ]

        losses_list = [
            abs(outcome.pnl)
            for _, outcome, _ in matches
            if outcome.pnl < 0
        ]

        holdings = [
            outcome.holding_minutes
            for _, outcome, _ in matches
        ]

        similarity_scores = [
            sim.score
            for _, _, sim in matches
        ]

        matched_predictions = [
            pred.prediction_id
            for pred, _, _ in matches
        ]

        win_rate = (
            round((wins / len(matches)) * 100, 2)
            if matches else 0.0
        )

        avg_profit = round(mean(profits), 2) if profits else 0.0
        avg_loss = round(mean(losses_list), 2) if losses_list else 0.0
        avg_hold = round(mean(holdings), 2) if holdings else 0.0

        weighted_similarity = 0

        total_weight = 0

        for _, outcome, similarity in matches:
            weight = max(

                1,

                similarity.score / 10,

            )

            weighted_similarity += (

                    similarity.score * weight

            )

            total_weight += weight

        avg_similarity = (

                weighted_similarity /

                total_weight

        )

        base_bonus = self.similarity.confidence_bonus(
            avg_similarity
        )

        confidence_bonus = base_bonus

        pattern_confidence = self._pattern_confidence(

            matches=len(matches),

            win_rate=win_rate,

            average_similarity=avg_similarity,

            average_profit=avg_profit,

        )

        if win_rate >= 80:

            recommendation = "STRONG_BUY"

        elif win_rate >= 60:

            recommendation = "BUY"

        elif win_rate <= 20:

            recommendation = "STRONG_SELL"

        elif win_rate <= 40:

            recommendation = "SELL"

        else:

            recommendation = "HOLD"

        analysis = PatternAnalysis(

            pattern_key=fingerprint,

            fingerprint=fingerprint,

            historical_matches=len(matches),

            wins=wins,

            losses=losses,

            win_rate=win_rate,

            average_profit=avg_profit,

            average_loss=avg_loss,

            average_holding_minutes=avg_hold,

            confidence_bonus=confidence_bonus,

            pattern_confidence=pattern_confidence,

            recommendation=recommendation,

            matched_predictions=matched_predictions,

            similarity_scores=similarity_scores,

            notes=[

                f"Average Similarity: {avg_similarity:.2f}%",

                "Generated by PatternMemory V2"

            ]

        )

        self._update_knowledge(
            fingerprint,
            analysis,
        )

        return analysis

    # =====================================================
    # Load Pattern Index
    # =====================================================

    def _load_pattern_index(self):

        """
        Load historical trades into memory.

        Executed only once.
        """

        if self.index_loaded:

            return

        history = self.storage.recent_predictions(
            limit=100000
        )

        for prediction in history:

            features = self.extractor.extract(
                prediction
            )

            signature = self._build_signature(
                features
            )

            self.pattern_index[
                signature
            ].append(
                prediction
            )

        self.index_loaded = True

    # =====================================================
    # Build Signature
    # =====================================================

    def _build_signature(

        self,

        features,

    ) -> str:

        """
        Build fast lookup key.

        Much smaller than fingerprint.
        """

        return "|".join(

            [

                features.decision,

                features.price_action,

                features.live_market,

                features.options,

                features.global_market,

                features.trend,

            ]

        )

    # =====================================================
    # Cache Lookup
    # =====================================================

    def _cache_lookup(
        self,
        fingerprint: str,
    ) -> PatternAnalysis | None:

        result = self.pattern_cache.get(
            fingerprint
        )

        if result is not None:

            self.cache_hits += 1

            return result

        self.cache_misses += 1

        return None

    # =====================================================
    # Cache Save
    # =====================================================

    def _cache_save(

        self,

        fingerprint: str,

        analysis: PatternAnalysis,

    ):

        self.pattern_cache[
            fingerprint
        ] = analysis

    # =====================================================
    # Clear Cache
    # =====================================================

    def clear_cache(self):

        self.pattern_cache.clear()


    # =====================================================
    # Cache Statistics
    # =====================================================

    def cache_statistics(self):

        total = self.cache_hits + self.cache_misses

        hit_rate = (

            self.cache_hits / total * 100

            if total

            else 0

        )

        return {

            "entries": len(self.pattern_cache),

            "hits": self.cache_hits,

            "misses": self.cache_misses,

            "hit_rate": round(hit_rate,2),

        }

    # =====================================================
    # Learn Pattern
    # =====================================================

    def _learn_pattern(

        self,

        fingerprint: str,

        analysis: PatternAnalysis,

    ):

        if not self.learning_enabled:

            return

        from datetime import datetime

        self.knowledge_base[fingerprint] = LearnedPattern(

            fingerprint=fingerprint,

            matches=analysis.historical_matches,

            wins=analysis.wins,

            losses=analysis.losses,

            win_rate=analysis.win_rate,

            average_profit=analysis.average_profit,

            average_loss=analysis.average_loss,

            confidence_bonus=analysis.confidence_bonus,

            recommendation=analysis.recommendation,

            age_score=100.0,

            last_updated=datetime.now(),

        )

    # =====================================================
    # Get Learned Pattern
    # =====================================================

    def get_learned_pattern(

        self,

        fingerprint: str,

    ):

        return self.knowledge_base.get(

            fingerprint

        )

    # =====================================================
    # Knowledge Statistics
    # =====================================================

    def knowledge_statistics(self):

        return {

            "patterns":

                len(self.knowledge_base),

            "learning":

                self.learning_enabled,

        }

    # =====================================================
    # Update Pattern Age
    # =====================================================

    def update_pattern_age(self):

        """
        Reduce confidence of old patterns.
        """

        from datetime import datetime

        for pattern in self.knowledge_base.values():

            if pattern.last_updated is None:
                continue

            age_days = (

                    datetime.now()

                    - pattern.last_updated

            ).days

            decay = age_days * 0.25

            pattern.age_score = max(

                25.0,

                100.0 - decay,

            )

    # =====================================================
    # Effective Confidence Bonus
    # =====================================================

    def effective_confidence_bonus(

        self,

        fingerprint: str,

    ) -> float:

        pattern = self.knowledge_base.get(

            fingerprint

        )

        if pattern is None:

            return 0

        return (

                pattern.confidence_bonus

                *

                pattern.age_score

                / 100.0

        )

    # =====================================================
    # Maintenance
    # =====================================================

    def maintenance(self):

        self.update_pattern_age()

        self.clear_cache()

    # =====================================================
    # Load Knowledge Base
    # =====================================================

    def load_knowledge_base(self):

        """
        Load learned patterns from storage.
        """

        self.knowledge_base.clear()

        patterns = self.storage.top_patterns(
            limit=100000
        )

        for pattern in patterns:
            self.knowledge_base[
                pattern.pattern_key
            ] = LearnedPattern(

                fingerprint=pattern.pattern_key,

                matches=pattern.total_occurrences,

                wins=pattern.wins,

                losses=pattern.losses,

                win_rate=pattern.win_rate,

                average_profit=pattern.average_profit,

                average_loss=pattern.average_loss,

                confidence_bonus=0.0,

                recommendation="HOLD",

                age_score=100.0,

                last_updated=None,

            )

    # =====================================================
    # Update Knowledge
    # =====================================================

    def _update_knowledge(

        self,

        fingerprint,

        analysis,

    ):

        self._learn_pattern(

            fingerprint,

            analysis,

        )

        pattern = self.storage.find_pattern(

            fingerprint

        )

        if pattern is None:

            return

        pattern.total_occurrences = (

            analysis.historical_matches

        )

        pattern.wins = analysis.wins

        pattern.losses = analysis.losses

        pattern.win_rate = analysis.win_rate

        pattern.average_profit = (

            analysis.average_profit

        )

        pattern.average_loss = (

            analysis.average_loss

        )

        self.storage.save_pattern(
            pattern
        )

    # =====================================================
    # Save All
    # =====================================================

    def save(self):

        """
        Persist everything.
        """

        for fingerprint,data in self.knowledge_base.items():

            pattern=self.storage.find_pattern(
                fingerprint
            )

            if pattern is None:

                continue

            self.storage.save_pattern(
                pattern
            )