"""
Trading Market AI V2

Similarity Engine

Compares historical market setups with the
current market.

Author : Super Cat
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .models import MarketFeatures


# ==========================================================
# Result
# ==========================================================

@dataclass
class SimilarityResult:
    """
    Result of comparing two market setups.
    """

    score: float

    matched_features: int

    total_features: int

    confidence_bonus: float

    matched: list[str] = field(default_factory=list)

    partial_matches: dict[str, float] = field(default_factory=dict)

    missed: list[str] = field(default_factory=list)

# ==========================================================
# Engine
# ==========================================================

class SimilarityEngine:

    """
    Calculates similarity between two
    MarketFeatures.
    """

    def __init__(self):

        self.base_weights = {

            "decision": 5,

            "price_action": 5,

            "live_market": 4,

            "options": 4,

            "global_market": 3,

            "trend": 5,

            "atr_bucket": 2,

            "vix_bucket": 2,

            "market_session": 1,

            "confidence_bucket": 2,

            "brain_agreement": 4,

        }

        self.dynamic_weights = {

            key: 1.0

            for key in self.base_weights

        }

    def _normalize_score(
            self,
            score: float,
            max_score: float,
    ) -> float:
        """
        Convert raw score into percentage.
        """

        if max_score <= 0:
            return 0.0

        return round((score / max_score) * 100, 2)

    def _clamp(
            self,
            value: float,
            minimum: float = 0.0,
            maximum: float = 1.0,
    ) -> float:
        """
        Keep value between minimum and maximum.
        """

        return max(minimum, min(maximum, value))

    def _bucket_similarity(
            self,
            current: str,
            historical: str,
    ) -> float:
        """
        Calculate similarity between bucket values.

        Returns:
            1.0 = Exact Match
            0.75 = Very Close
            0.50 = Close
            0.25 = Weak Match
            0.00 = Completely Different
        """

        if current == historical:
            return 1.0

        order = [
            "VERY_LOW",
            "LOW",
            "MEDIUM",
            "HIGH",
            "VERY_HIGH",
        ]

        try:

            current_index = order.index(current)
            historical_index = order.index(historical)

        except ValueError:
            return 0.0

        distance = abs(current_index - historical_index)

        if distance == 1:
            return 0.75

        if distance == 2:
            return 0.50

        if distance == 3:
            return 0.25

        return 0.0

    def _add_bucket_score(
            self,
            current: str,
            historical: str,
            weight: float,
            score: float,
            matched: int,
    ) -> tuple[float, int]:
        """
        Add weighted bucket similarity.

        Returns:
            Updated score
            Updated matched count
        """

        similarity = self._bucket_similarity(
            current,
            historical,
        )

        score += similarity * weight

        if similarity > 0:
            matched += 1

        return score, matched

    def _numeric_similarity(
            self,
            current: float,
            historical: float,
            maximum_difference: float,
    ) -> float:
        """
        Compare two numeric values.

        Returns
        -------
        1.0 = identical
        0.0 = completely different
        """

        difference = abs(current - historical)

        similarity = 1.0 - (difference / maximum_difference)

        return self._clamp(similarity)

    def _weight(
            self,
            feature: str,
    ) -> float:
        """
        Returns the effective weight for a feature.

        Effective Weight =
            Base Weight × Dynamic Weight
        """

        if feature not in self.base_weights:
            raise KeyError(
                f"Unknown feature weight: '{feature}'"
            )

        base = self.base_weights[feature]
        dynamic = self.dynamic_weights.get(feature, 1.0)

        return base * dynamic
    # ======================================================
    # Compare
    # ======================================================

    def compare(

        self,

        current: MarketFeatures,

        historical: MarketFeatures,

    ) -> SimilarityResult:

        score = 0.0
        matched_list = []

        partial_matches = {}

        missed = []

        maximum = sum(
            self._weight(feature)
            for feature in self.base_weights
        )

        matched = 0

        # -----------------------------------------------

        if current.decision == historical.decision:

            score += self._weight("decision")

            matched += 1

            matched_list.append("decision")

        else:

            missed.append("decision")

        if current.price_action == historical.price_action:

            score += self._weight("price_action")

            matched += 1

            matched_list.append("price_action")

        else:

            missed.append("price_action")

        if current.live_market == historical.live_market:

            score += self._weight("live_market")

            matched += 1

            matched_list.append("live_market")

        else:

            missed.append("live_market")

        if current.options == historical.options:

            score += self._weight("options")

            matched += 1

            matched_list.append("options")

        else:

            missed.append("options")

        if current.global_market == historical.global_market:

            score += self._weight("global_market")

            matched += 1

            matched_list.append("global_market")

        else:

            missed.append("global_market")

        if current.trend == historical.trend:

            score += self._weight("trend")

            matched += 1

            matched_list.append("trend")

        else:

            missed.append("trend")

        if current.market_session == historical.market_session:

            score += self._weight("market_session")

            matched += 1

            matched_list.append("market_session")

        else:

            missed.append("market_session")

        if current.brain_agreement == historical.brain_agreement:

            score += self._weight("brain_agreement")

            matched += 1

            matched_list.append("brain_agreement")

        else:

            missed.append("brain_agreement")

        vix_similarity = self._bucket_similarity(
            current.vix_bucket,
            historical.vix_bucket,
        )

        score += vix_similarity * self._weight("vix_bucket")

        if vix_similarity == 1.0:

            matched += 1

            matched_list.append("vix_bucket")

        elif vix_similarity > 0:

            matched += 1

            partial_matches["vix_bucket"] = vix_similarity

        else:

            missed.append("vix_bucket")

        atr_similarity = self._bucket_similarity(
            current.atr_bucket,
            historical.atr_bucket,
        )

        score += atr_similarity * self._weight("atr_bucket")

        if atr_similarity == 1.0:

            matched += 1

            matched_list.append("atr_bucket")

        elif atr_similarity > 0:

            matched += 1

            partial_matches["atr_bucket"] = atr_similarity

        else:

            missed.append("atr_bucket")


        confidence_similarity = self._numeric_similarity(
            current.confidence,
            historical.confidence,
            maximum_difference=100,
        )

        score += (
                confidence_similarity
                * self._weight("confidence_bucket")
        )

        if confidence_similarity == 1.0:

            matched += 1

            matched_list.append("confidence")

        elif confidence_similarity > 0:

            matched += 1

            partial_matches["confidence"] = confidence_similarity

        else:

            missed.append("confidence")


        similarity = self._normalize_score(
            score,
            maximum,
        )

        return SimilarityResult(

            score=similarity,

            matched_features=matched,

            total_features=len(self.base_weights),

            confidence_bonus=self.confidence_bonus(
                similarity
            ),

            matched=matched_list,

            partial_matches=partial_matches,

            missed=missed,

        )

    # ======================================================
    # Confidence Bonus
    # ======================================================

    @staticmethod
    def confidence_bonus(
        similarity: float,
    ) -> float:

        if similarity >= 95:

            return 10

        if similarity >= 90:

            return 8

        if similarity >= 80:

            return 6

        if similarity >= 70:

            return 4

        if similarity >= 60:

            return 2

        return 0

    # ======================================================
    # Best Match
    # ======================================================

    def best_match(

        self,

        current: MarketFeatures,

        history: List[MarketFeatures],

    ):

        best = None

        highest = -1

        for historical in history:

            result = self.compare(

                current,

                historical,

            )

            if result.score > highest:

                highest = result.score

                best = (

                    historical,

                    result,

                )

        return best

    # ======================================================
    # Top Matches
    # ======================================================

    def top_matches(

        self,

        current: MarketFeatures,

        history: List[MarketFeatures],

        minimum_score: float = 70,

    ):

        matches = []

        for historical in history:

            result = self.compare(

                current,

                historical,

            )

            if result.score >= minimum_score:

                matches.append(

                    (

                        historical,

                        result,

                    )

                )

        matches.sort(

            key=lambda x: x[1].score,

            reverse=True,

        )

        return matches