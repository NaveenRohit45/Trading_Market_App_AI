from backend.analyzers.market_analyzer import analyze


class PriceActionBrain:

    TIMEFRAME_WEIGHTS = {
        "1m": 0.20,
        "2m": 0.20,
        "3m": 0.30,
        "5m": 0.30,
    }


    def analyze(
        self,
        symbol,
        candles,
    ):

        timeframe_results = {}

        for timeframe in (
            "1m",
            "2m",
            "3m",
            "5m",
        ):

            timeframe_results[timeframe] = (
                self._analyze_timeframe(
                    symbol,
                    timeframe,
                    candles.get(
                        timeframe,
                        [],
                    ),
                )
            )


        ready_results = {
            timeframe: result
            for timeframe, result
            in timeframe_results.items()
            if result["status"] == "READY"
        }


        if not ready_results:

            return {
                "brain": "PRICE_ACTION",
                "symbol": symbol,
                "status": "WARMING_UP",
                "direction": "NEUTRAL",
                "confidence": 0,
                "score": 0,
                "structure": "UNKNOWN",
                "setup": "WAIT",
                "reasons": [
                    "Collecting real multi-timeframe candles"
                ],
                "contradictions": [],
                "invalidation": None,
                "timeframes": timeframe_results,
            }


        weighted_score = 0.0
        active_weight = 0.0

        bullish_timeframes = []
        bearish_timeframes = []
        neutral_timeframes = []


        for timeframe, result in ready_results.items():

            weight = self.TIMEFRAME_WEIGHTS[
                timeframe
            ]

            weighted_score += (
                result["score"]
                * weight
            )

            active_weight += weight


            if result["direction"] == "BULLISH":

                bullish_timeframes.append(
                    timeframe
                )

            elif result["direction"] == "BEARISH":

                bearish_timeframes.append(
                    timeframe
                )

            else:

                neutral_timeframes.append(
                    timeframe
                )


        if active_weight > 0:

            final_score = (
                weighted_score
                / active_weight
            )

        else:

            final_score = 0


        final_score = round(
            max(
                -100,
                min(
                    100,
                    final_score,
                ),
            ),
            1,
        )


        reasons = []
        contradictions = []


        # ------------------------------------------
        # MULTI-TIMEFRAME AGREEMENT
        # ------------------------------------------

        if len(bullish_timeframes) >= 3:

            reasons.append(
                "Bullish agreement across "
                + ", ".join(
                    bullish_timeframes
                )
            )


        if len(bearish_timeframes) >= 3:

            reasons.append(
                "Bearish agreement across "
                + ", ".join(
                    bearish_timeframes
                )
            )


        # ------------------------------------------
        # FAST VS SLOW CONTRADICTION
        # ------------------------------------------

        one_minute = timeframe_results["1m"]
        five_minute = timeframe_results["5m"]


        if (
            one_minute["status"] == "READY"
            and five_minute["status"] == "READY"
            and one_minute["direction"]
            != five_minute["direction"]
            and one_minute["direction"]
            != "NEUTRAL"
            and five_minute["direction"]
            != "NEUTRAL"
        ):

            contradictions.append(
                "1m direction conflicts with 5m structure"
            )


        # ------------------------------------------
        # FINAL DIRECTION
        # ------------------------------------------

        if final_score >= 30:

            direction = "BULLISH"

        elif final_score <= -30:

            direction = "BEARISH"

        else:

            direction = "NEUTRAL"


        # ------------------------------------------
        # SETUP STATE
        # ------------------------------------------

        setup = "WAIT"


        if (
            direction == "BULLISH"
            and len(bullish_timeframes) >= 3
        ):

            setup = "CALL_SETUP"


        elif (
            direction == "BEARISH"
            and len(bearish_timeframes) >= 3
        ):

            setup = "PUT_SETUP"


        # A setup is not an entry if major timeframes conflict.

        if contradictions:

            setup = "WAIT"


        # ------------------------------------------
        # CONFIDENCE
        # ------------------------------------------

        confidence = min(
            95,
            abs(final_score),
        )


        agreement_count = max(
            len(bullish_timeframes),
            len(bearish_timeframes),
        )


        if agreement_count == 4:

            confidence = min(
                95,
                confidence + 10,
            )


        if contradictions:

            confidence = max(
                0,
                confidence - (
                    len(contradictions)
                    * 15
                ),
            )


        confidence = round(
            confidence,
            1,
        )


        # ------------------------------------------
        # INVALIDATION
        # Prefer stronger 5m structure.
        # ------------------------------------------

        invalidation = None


        if five_minute["status"] == "READY":

            invalidation = five_minute[
                "invalidation"
            ]

        elif one_minute["status"] == "READY":

            invalidation = one_minute[
                "invalidation"
            ]


        return {
            "brain": "PRICE_ACTION",
            "symbol": symbol,
            "status": "READY",
            "direction": direction,
            "confidence": confidence,
            "score": final_score,
            "structure": (
                five_minute.get(
                    "structure",
                    "UNKNOWN",
                )
            ),
            "setup": setup,
            "reasons": reasons,
            "contradictions": contradictions,
            "invalidation": invalidation,
            "agreement": {
                "bullish": bullish_timeframes,
                "bearish": bearish_timeframes,
                "neutral": neutral_timeframes,
            },
            "timeframes": timeframe_results,
        }


    def _analyze_timeframe(
        self,
        symbol,
        timeframe,
        candles,
    ):

        if len(candles) < 6:

            return {
                "timeframe": timeframe,
                "status": "WARMING_UP",
                "direction": "NEUTRAL",
                "score": 0,
                "structure": "UNKNOWN",
                "invalidation": None,
                "candle_count": len(candles),
            }


        base = analyze(
            symbol,
            candles,
        )


        score = 0
        reasons = []
        contradictions = []


        # ------------------------------------------
        # EMA STRUCTURE
        # ------------------------------------------

        if (
            base["price"]
            > base["ema_fast"]
            > base["ema_slow"]
        ):

            score += 25

            reasons.append(
                "Price above fast and slow EMA"
            )


        elif (
            base["price"]
            < base["ema_fast"]
            < base["ema_slow"]
        ):

            score -= 25

            reasons.append(
                "Price below fast and slow EMA"
            )


        else:

            contradictions.append(
                "EMA structure mixed"
            )


        # ------------------------------------------
        # MOMENTUM
        # ------------------------------------------

        if base["momentum"] > 0:

            score += 15

            reasons.append(
                "Positive momentum"
            )


        elif base["momentum"] < 0:

            score -= 15

            reasons.append(
                "Negative momentum"
            )


        # ------------------------------------------
        # RSI
        # ------------------------------------------

        rsi = base["rsi"]


        if 55 <= rsi <= 75:

            score += 15

            reasons.append(
                "RSI supports bullish momentum"
            )


        elif 25 <= rsi <= 45:

            score -= 15

            reasons.append(
                "RSI supports bearish momentum"
            )


        elif rsi > 75:

            contradictions.append(
                f"RSI overextended ({rsi})"
            )


        elif rsi < 25:

            contradictions.append(
                f"RSI deeply oversold ({rsi})"
            )


        # ------------------------------------------
        # BREAKOUT
        # ------------------------------------------

        if base["breakout"] == "UP":

            score += 25

            reasons.append(
                "Breakout above resistance"
            )


        elif base["breakout"] == "DOWN":

            score -= 25

            reasons.append(
                "Breakdown below support"
            )


        # ------------------------------------------
        # REGIME
        # ------------------------------------------

        if base["regime"] == "TRENDING":

            if score > 0:

                score += 10

            elif score < 0:

                score -= 10


        else:

            contradictions.append(
                "Choppy regime"
            )


        # ------------------------------------------
        # CANDLE STRUCTURE
        # ------------------------------------------

        recent = candles[-4:]

        highs = [
            candle.high
            for candle in recent
        ]

        lows = [
            candle.low
            for candle in recent
        ]


        higher_highs = all(
            highs[i] > highs[i - 1]
            for i in range(
                1,
                len(highs),
            )
        )


        higher_lows = all(
            lows[i] > lows[i - 1]
            for i in range(
                1,
                len(lows),
            )
        )


        lower_highs = all(
            highs[i] < highs[i - 1]
            for i in range(
                1,
                len(highs),
            )
        )


        lower_lows = all(
            lows[i] < lows[i - 1]
            for i in range(
                1,
                len(lows),
            )
        )


        structure = "MIXED"


        if higher_highs and higher_lows:

            structure = "HH_HL"

            score += 20

            reasons.append(
                "Higher highs and higher lows"
            )


        elif lower_highs and lower_lows:

            structure = "LH_LL"

            score -= 20

            reasons.append(
                "Lower highs and lower lows"
            )


        else:

            contradictions.append(
                "Mixed candle structure"
            )


        score = max(
            -100,
            min(
                100,
                score,
            ),
        )


        if score >= 30:

            direction = "BULLISH"

        elif score <= -30:

            direction = "BEARISH"

        else:

            direction = "NEUTRAL"


        if direction == "BULLISH":

            invalidation = base["support"]

        elif direction == "BEARISH":

            invalidation = base["resistance"]

        else:

            invalidation = None


        return {
            "timeframe": timeframe,
            "status": "READY",
            "direction": direction,
            "score": score,
            "structure": structure,
            "invalidation": invalidation,
            "candle_count": len(candles),
            "reasons": reasons,
            "contradictions": contradictions,
            "signals": base,
        }