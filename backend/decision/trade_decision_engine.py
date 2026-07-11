from dataclasses import dataclass
from typing import Optional

from backend.decision.trade_state import (
    TradeDecision,
    TradeState,
    TradeBias,
    MarketCondition,
)

from backend.decision.confidence_engine import (
    BrainOpinion,
    confidence_engine,
)

from backend.decision.risk_manager import (
    risk_manager,
)


# ==========================================================
# DECISION CONTEXT
# ==========================================================

@dataclass
class DecisionContext:

    symbol: str

    price: float

    support: Optional[float]

    resistance: Optional[float]

    atr: float

    price_action: dict

    timestamp: float = 0.0


# ==========================================================
# TRADE DECISION ENGINE
# ==========================================================

class TradeDecisionEngine:

    def __init__(self):

        self.ready_threshold = 65

        self.enter_threshold = 80

    # ------------------------------------------------------
    # MARKET CONDITION
    # ------------------------------------------------------

    def _market_condition(
        self,
        direction,
    ):

        if direction == "BULLISH":

            return MarketCondition.TRENDING_BULLISH

        if direction == "BEARISH":

            return MarketCondition.TRENDING_BEARISH

        return MarketCondition.SIDEWAYS

    # ------------------------------------------------------
    # MAIN DECISION
    # ------------------------------------------------------

    def decide(
        self,
        ctx: DecisionContext,
    ) -> TradeDecision:

        pa = ctx.price_action

        opinions = {

            "price_action": BrainOpinion(

                name="Price Action",

                direction=pa["direction"],

                confidence=pa["confidence"],

                weight=1.0,

                reasons=pa.get(
                    "reasons",
                    [],
                ),

                contradictions=pa.get(
                    "contradictions",
                    [],
                ),
            )

        }

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        conf = confidence_engine.calculate(
            opinions
        )

        # --------------------------------------------------
        # RISK
        # --------------------------------------------------

        risk = risk_manager.assess(

            direction=pa["direction"],

            price=ctx.price,

            support=ctx.support,

            resistance=ctx.resistance,

            atr=ctx.atr,

            confidence=conf.confidence,

        )

        # --------------------------------------------------
        # BUILD DECISION
        # --------------------------------------------------

        d = TradeDecision()

        d.symbol = ctx.symbol

        d.timestamp = ctx.timestamp

        d.market_condition = self._market_condition(
            pa["direction"]
        )

        d.confidence = conf.confidence

        d.risk = risk.risk_level

        d.entry_price = risk.entry

        d.stop_loss = risk.stop_loss

        d.invalidation = risk.stop_loss

        d.target1 = risk.target1

        d.target2 = risk.target2

        d.reward_risk_ratio = (
            risk.reward_risk_ratio
        )

        # --------------------------------------------------
        # ENTRY ZONE
        # --------------------------------------------------

        if d.entry_price is not None:

            spread = ctx.atr * 0.20

            d.entry_zone_low = round(

                d.entry_price - spread,

                2,

            )

            d.entry_zone_high = round(

                d.entry_price + spread,

                2,

            )

        # --------------------------------------------------
        # EXPECTED MOVE
        # --------------------------------------------------

        if (

            d.entry_price is not None

            and

            d.target1 is not None

        ):

            d.expected_points = round(

                abs(

                    d.target1

                    -

                    d.entry_price

                ),

                2,

            )

        d.expected_move_minutes = 5

        # --------------------------------------------------
        # REASONS
        # --------------------------------------------------

        d.reasons.extend(

            conf.reasons

        )

        d.warnings.extend(

            risk.warnings

        )

        d.contradictions.extend(

            conf.warnings

        )

        # --------------------------------------------------
        # SOURCE BRAINS
        # --------------------------------------------------

        d.source_brains = [

            "PRICE_ACTION",

        ]

        # --------------------------------------------------
        # PRICE ACTION SETUP
        # --------------------------------------------------

        setup = pa.get(
            "setup",
            "WAIT",
        )

        # --------------------------------------------------
        # NO SETUP -> WAIT
        # --------------------------------------------------

        if setup == "WAIT":
            d.state = TradeState.WAIT

            d.bias = TradeBias.NONE

            d.reasons.append(
                "Price Action Brain suggests waiting."
            )

            return d

        # --------------------------------------------------
        # RISK MANAGER
        # --------------------------------------------------

        if not risk.can_trade:
            d.state = TradeState.AVOID

            d.bias = TradeBias.NONE

            d.warnings.append(
                "Risk Manager rejected trade."
            )

            return d

        # --------------------------------------------------
        # BIAS
        # --------------------------------------------------

        if setup == "CALL_SETUP":

            d.bias = TradeBias.CALL

        elif setup == "PUT_SETUP":

            d.bias = TradeBias.PUT

        else:

            d.bias = TradeBias.NONE

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------

        if conf.confidence < self.ready_threshold:

            d.state = TradeState.WAIT

            d.warnings.append(

                "Confidence below READY threshold."

            )

        elif (

            conf.confidence

            <

            self.enter_threshold

        ):

            d.state = TradeState.READY

            d.reasons.append(

                "Setup is forming."

            )

        else:

            d.state = TradeState.ENTER

            d.reasons.append(

                "All conditions satisfied."

            )

        return d


# ==========================================================
# SINGLETON
# ==========================================================

trade_decision_engine = TradeDecisionEngine()