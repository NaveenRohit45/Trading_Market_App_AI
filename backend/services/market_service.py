import asyncio
import time
from collections import deque
from dataclasses import asdict, is_dataclass
from enum import Enum

from backend.config import settings
from backend.core.candle_engine import CandleEngine
from backend.analyzers.market_analyzer import analyze
from backend.analyzers.news_analyzer import NewsAnalyzer
from backend.models import NewsInput
from backend.prediction.prediction_engine import predict, combined_verdict
from backend.prediction.ml_predictor import predict_ml
from backend.ai.ai_summary import generate_ai_summary
from backend.prediction.adaptive_confidence import combine_adaptive_verdict
from backend.prediction.regime_detector import detect_regime
from backend.data.options_provider import OptionsFlowProvider
from backend.data.news_ingestor import AutoNewsIngestor
import httpx
from backend.services.database import Database
from backend.data.demo_provider import DemoProvider
from backend.data.groww_provider import GrowwProvider
from backend.brains.price_action.price_action_brain import PriceActionBrain
from backend.decision.trade_decision_engine import (
    DecisionContext,
    trade_decision_engine,
)
from datetime import datetime, date
from backend.brains.live_market.live_market_brain import (
    LiveMarketBrain,
)

from backend.brains.global_market.global_market_brain import (
    GlobalMarketBrain,
)

from backend.services.historical_loader import HistoricalLoader

class MarketService:

    def __init__(self):

        self.provider = (
            GrowwProvider()
            if settings.app_mode == "GROWW"
            else DemoProvider()
        )
        self.price_action_brain = PriceActionBrain()
        self.engine = CandleEngine()

        # Pass the live Groww connection into the historical loader so it
        # pulls candles from Groww (fast, reliable) instead of Yahoo
        # Finance, whenever we're actually running in GROWW mode.
        groww_provider_for_history = (
            self.provider if settings.app_mode == "GROWW" else None
        )

        self.history = HistoricalLoader(
            self.engine,
            groww_provider=groww_provider_for_history,
        )
        self.news = NewsAnalyzer()
        self.db = Database(settings.db_path)

        self.clients = set()

        self.latest = {}

        self.last_live_brains = {
            "price_action": {},
            "live_market": {},
            "global_market": {},
            "decision": {},
        }

        self.last_status = None

        self.last_prediction = 0
        self.last_alert_key = None

        self.running = False
        self.error = None

        self.alerts = deque(maxlen=20)

        self.loop_task = None

        self.last_live_brains = {
            "price_action": {},
            "live_market": {},
            "global_market": {},
            "decision": {},
        }
        self.live_market_analysis = None

        # Real AI reasoning layer (Claude). Runs on a slow cadence,
        # separate from the live tick loop -- see handle_live_snapshot.
        self._ai_http_client = httpx.AsyncClient()
        self.ai_summaries = {}
        self.last_ai_summary_time = 0

        # Options flow (PCR + OI shift) -- a genuinely new signal
        # source, only available when we have a real Groww connection.
        self.options_provider = (
            OptionsFlowProvider(self.provider.groww)
            if settings.app_mode == "GROWW" and hasattr(self.provider, "groww")
            else None
        )
        self.options_analysis = {}
        self.last_options_fetch_time = 0

        self.news_ingestor = AutoNewsIngestor()
        self.last_news_fetch_time = 0

        self.last_regime = {}  # {symbol: regime} -- for change detection

    async def start(self):

        print("=" * 60)
        print("STARTING ADA MARKET SERVICE")
        print(f"MODE: {settings.app_mode}")
        print("=" * 60)

        # --------------------------------------------------
        # LOAD HISTORICAL CANDLES
        # --------------------------------------------------

        print("=" * 60)
        print("Loading Historical Market Data...")
        print("=" * 60)

        results = self.history.load_multiple(
            symbols=[
                "NIFTY",
                "SENSEX",
            ]
        )

        print()

        for symbol, stats in results.items():

            if stats is None:
                print(f"❌ {symbol} Failed")
                continue

            print(
                f"✅ {symbol} | "
                f"1m={stats['1m']} "
                f"2m={stats['2m']} "
                f"3m={stats['3m']} "
                f"5m={stats['5m']}"
            )

        print("=" * 60)
        print("Historical Loading Completed")
        print("=" * 60)

        self.running = True

        self.loop_task = asyncio.create_task(
            self.loop()
        )

        print(
            "✅ Market service background loop started"
        )


    async def stop(self):

        print(
            "Stopping ADA Market Service..."
        )

        self.running = False

        if self.loop_task:

            self.loop_task.cancel()

            try:

                await self.loop_task

            except asyncio.CancelledError:

                pass

        await self.provider.stop()

        print(
            "🛑 ADA Market Service stopped"
        )


    async def loop(self):

        while self.running:

            try:

                now = time.time()

                # --------------------------------------------------
                # GET PROVIDER SNAPSHOT
                # --------------------------------------------------

                provider_snapshot = (
                    await self.provider.get_prices()
                )


                if not isinstance(
                    provider_snapshot,
                    dict,
                ):

                    raise RuntimeError(
                        "Groww provider returned invalid data"
                    )


                status = provider_snapshot.get(
                    "status"
                )

                prices = provider_snapshot.get(
                    "prices",
                    {},
                )


                # ==================================================
                # LIVE MARKET
                # ==================================================

                if status == "LIVE":

                    await self.handle_live_snapshot(
                        prices=prices,
                        now=now,
                        provider_snapshot=provider_snapshot,
                    )


                # ==================================================
                # MARKET CLOSED
                # ==================================================

                elif status == "MARKET_CLOSED":

                    await self.handle_market_closed(
                        prices=prices,
                        now=now,
                        provider_snapshot=provider_snapshot,
                    )


                # ==================================================
                # UNKNOWN PROVIDER STATE
                # ==================================================

                else:

                    raise RuntimeError(
                        f"Unknown Groww provider status: {status}"
                    )


            except asyncio.CancelledError:

                raise


            except Exception as error:

                await self.handle_feed_error(
                    error
                )


            await asyncio.sleep(
                settings.poll_seconds
            )


    async def handle_live_snapshot(
        self,
        prices,
        now,
        provider_snapshot,
    ):

        # --------------------------------------------------
        # VALIDATE REAL LIVE PRICES
        # --------------------------------------------------

        if "NIFTY" not in prices:

            raise RuntimeError(
                "NIFTY missing from live Groww snapshot"
            )


        if "SENSEX" not in prices:

            raise RuntimeError(
                "SENSEX missing from live Groww snapshot"
            )


        nifty_price = float(
            prices["NIFTY"]
        )

        sensex_price = float(
            prices["SENSEX"]
        )


        if nifty_price <= 0:

            raise RuntimeError(
                "Invalid NIFTY live price"
            )


        if sensex_price <= 0:

            raise RuntimeError(
                "Invalid SENSEX live price"
            )


        prices = {
            "NIFTY": nifty_price,
            "SENSEX": sensex_price,
        }


        # --------------------------------------------------
        # REAL LIVE DATA CONFIRMED
        # --------------------------------------------------

        self.error = None


        # Only genuine live prices enter CandleEngine.
        for symbol, price in prices.items():

            # BUILD REAL MULTI-TIMEFRAME CANDLES
            for interval in (
                    60,  # 1 minute
                    120,  # 2 minutes
                    180,  # 3 minutes
                    300,  # 5 minutes
            ):
                self.engine.add_tick(
                    symbol,
                    price,
                    now,
                    interval,
                )


        # Only genuine live prices resolve predictions.
        self.db.resolve(
            now,
            prices,
        )

        # Resolve each brain's individual calls too -- this is what
        # feeds the Adaptive Confidence Engine's rolling accuracy.
        self.db.resolve_brain_calls(
            now,
            prices,
        )


        self.latest = self.build_live_snapshot(
            prices,
            now,
        )

        # Attach the most recently generated AI summaries (may be from
        # a few minutes ago -- that's expected, they run on a slower
        # cadence than the price tick loop).
        self.latest["ai_summaries"] = self.ai_summaries

        print("LIVE SNAPSHOT CREATED")
        # print(self.latest["brains"])
        # Save last live AI brains
        self.last_live_brains = self.latest.get(
            "brains",
            self.last_live_brains,
        )

        # Persist closed 1-minute candles every cycle (cheap,
        # INSERT OR IGNORE dedupes automatically) -- this is the raw
        # data train_lstm.py needs. Doing this every tick is fine
        # since duplicates are just ignored.
        for candle_symbol in ("NIFTY", "SENSEX"):
            closed_candles = self.engine.series(
                candle_symbol, 60, include_current=False
            )
            for candle in closed_candles[-3:]:  # last few, cheap dedupe insert
                self.db.add_candle(
                    candle_symbol,
                    candle.start_ts,
                    candle.open,
                    candle.high,
                    candle.low,
                    candle.close,
                    candle.volume,
                )

        if (
            now - self.last_prediction
            >= settings.prediction_interval_seconds
        ):

            self.store_predictions(
                now
            )

            self.last_prediction = now

        # Automated news ingestion from free RSS feeds -- runs on
        # the same slow cadence, fails safe if feeds are unreachable.
        if now - self.last_news_fetch_time >= settings.prediction_interval_seconds:
            self.last_news_fetch_time = now
            try:
                for item in self.news_ingestor.fetch_new_items():
                    self.news.add(NewsInput(**item))
            except Exception as error:
                print(f"⚠️ Auto news ingestion failed: {error}")

        # Options flow (PCR/OI) -- also slow cadence, real API cost.
        if (
            self.options_provider is not None
            and now - self.last_options_fetch_time >= settings.prediction_interval_seconds
        ):
            self.last_options_fetch_time = now
            for opt_symbol in ("NIFTY", "SENSEX"):
                try:
                    result = self.options_provider.analyze(opt_symbol)
                    if result is not None:
                        self.options_analysis[opt_symbol] = result
                except Exception as error:
                    print(f"⚠️ Options analysis failed for {opt_symbol}: {error}")

        # Real AI reasoning layer -- runs on the same slow cadence as
        # prediction storage (not every 3-second tick). Failures are
        # caught inside generate_ai_summary and never break the live
        # loop; if it fails you just keep the last good summary.
        if (
            now - self.last_ai_summary_time
            >= settings.prediction_interval_seconds
        ):

            self.last_ai_summary_time = now

            asyncio.create_task(
                self.refresh_ai_summaries(now)
            )


        self.detect_alert(
            now
        )


        await self.broadcast(
            self.latest
        )


        print(
            "📡 LIVE GROWW SNAPSHOT | "
            f"NIFTY: {nifty_price} | "
            f"SENSEX: {sensex_price}"
        )


    def compute_adaptive_verdict(self, symbol, analysis, price_action, forecasts, now, prices):
        """
        Gathers every brain's current vote for this symbol, normalizes
        their direction vocabulary (price-action uses
        BULLISH/BEARISH/NEUTRAL; forecasts use UP/DOWN/SIDEWAYS -- the
        Adaptive Confidence Engine needs one consistent vocabulary),
        logs each vote to brain_calls for future accuracy scoring, and
        returns the reweighted verdict.
        """

        direction_map = {
            "BULLISH": "UP", "BEARISH": "DOWN", "NEUTRAL": "SIDEWAYS",
            "UP": "UP", "DOWN": "DOWN", "SIDEWAYS": "SIDEWAYS",
        }

        brain_votes = {}

        pa = price_action.get(symbol) or {}
        if pa.get("direction"):
            brain_votes["price_action"] = {
                "direction": direction_map.get(pa["direction"], "SIDEWAYS"),
                "confidence": pa.get("confidence", 50.0),
            }

        v1_list = forecasts.get(symbol) or []
        v1_three_min = next((f for f in v1_list if f.get("horizon") == 3), None)
        if v1_three_min:
            brain_votes["v1_heuristic"] = {
                "direction": direction_map.get(v1_three_min.get("direction"), "SIDEWAYS"),
                "confidence": v1_three_min.get("confidence", 50.0),
            }

        ml_list = forecasts.get(f"{symbol}_ML") or []
        ml_three_min = next((f for f in ml_list if f.get("horizon") == 3), None)
        if ml_three_min:
            brain_votes["ml_model"] = {
                "direction": direction_map.get(ml_three_min.get("direction"), "SIDEWAYS"),
                "confidence": ml_three_min.get("confidence", 50.0),
            }

        # Options flow (PCR + OI shift) -- genuinely new signal, votes
        # like every other brain and earns/loses trust the same way.
        options_data = self.options_analysis.get(symbol)
        if options_data and options_data.get("direction"):
            brain_votes["options_flow"] = {
                "direction": direction_map.get(options_data["direction"], "SIDEWAYS"),
                "confidence": options_data.get("confidence", 50.0),
            }

        current_regime = detect_regime(analysis)

        # Regime-change alert -- fires once per actual transition, not
        # every cycle (that would spam the alerts feed uselessly).
        previous_regime = self.last_regime.get(symbol)
        if (
            previous_regime is not None
            and current_regime != previous_regime
            and current_regime != "UNKNOWN"
        ):
            self.alerts.appendleft({
                "ts": now,
                "title": f"{symbol} regime change",
                "message": f"Shifted from {previous_regime} to {current_regime}.",
            })
        self.last_regime[symbol] = current_regime

        # Log each brain's call for future accuracy resolution (cheap
        # write, dedupe isn't needed since these are timestamped facts,
        # not idempotent state).
        price_now = prices.get(symbol)
        if price_now:
            for brain_name, vote in brain_votes.items():
                self.db.add_brain_call(
                    now, symbol, brain_name, 3, price_now,
                    vote["direction"],
                    regime=current_regime,
                )

        result = combine_adaptive_verdict(symbol, analysis, brain_votes, self.db)

        return result


    async def refresh_ai_summaries(self, now):
        """
        Calls Claude for a real reasoning-based summary of each
        symbol, using everything the app currently knows: technical
        snapshot, all rule-based brains, the V1 heuristic forecast,
        the ML model's forecast (if trained), and actual historical
        accuracy. Runs in the background so it never blocks the live
        price loop; updates self.ai_summaries when done, and the next
        broadcast will include it.
        """

        accuracy_stats = self.db.accuracy()

        for symbol in ("NIFTY", "SENSEX"):

            result = await generate_ai_summary(
                symbol,
                self.latest,
                accuracy_stats,
                self._ai_http_client,
            )

            self.ai_summaries[symbol] = result

        # Push the freshly generated summaries out immediately rather
        # than waiting for the next 3-second tick.
        if isinstance(self.latest, dict):
            self.latest["ai_summaries"] = self.ai_summaries
            await self.broadcast(self.latest)


    async def handle_market_closed(
        self,
        prices,
        now,
        provider_snapshot,
    ):

        # --------------------------------------------------
        # MARKET CLOSED IS NOT AN ERROR
        # --------------------------------------------------

        self.error = None

        saved_timestamp = (
            provider_snapshot.get(
                "timestamp"
            )
        )

        # --------------------------------------------------
        # SAVED LAST MARKET VALUES AVAILABLE
        # --------------------------------------------------

        if (
            "NIFTY" in prices
            and "SENSEX" in prices
        ):

            nifty_price = float(
                prices["NIFTY"]
            )

            sensex_price = float(
                prices["SENSEX"]
            )


            self.latest = {
                "ts": now,
                "mode": settings.app_mode,

                "status": "MARKET_CLOSED",
                "live": False,

                "prices": {
                    "NIFTY": nifty_price,
                    "SENSEX": sensex_price,
                },

                # IMPORTANT:
                # These are saved values.
                # Do not generate new analysis or predictions.
                "analysis": {},
                "brains": self.last_live_brains,
                "forecast": {},
                "combined": None,

                "news_score": self.news.score(),
                "news": self.news.latest(),

                "alerts": list(
                    self.alerts
                ),

                "error": None,

                "market_message": (
                    "Market closed. Showing last saved "
                    "genuine Groww market values."
                ),

                "last_live_timestamp": (
                    saved_timestamp
                ),

                "experimental": True,
            }

            print(
                "🌙 MARKET CLOSED | "
                "Showing last saved values | "
                f"NIFTY: {nifty_price} | "
                f"SENSEX: {sensex_price}"
            )


        # --------------------------------------------------
        # NO SAVED SNAPSHOT YET
        # --------------------------------------------------

        else:

            self.latest = {
                "ts": now,
                "mode": settings.app_mode,

                "status": "MARKET_CLOSED",
                "live": False,

                "prices": {},

                "analysis": {},
                "brains": self.last_live_brains,
                "forecast": {},
                "combined": None,

                "news_score": self.news.score(),
                "news": self.news.latest(),

                "alerts": list(
                    self.alerts
                ),

                "error": None,

                "market_message": (
                    "Market closed. No saved live snapshot "
                    "is available on this machine yet."
                ),

                "last_live_timestamp": None,

                "experimental": True,
            }


            print(
                "🌙 MARKET CLOSED | "
                "No saved live snapshot available"
            )


        await self.broadcast(
            self.latest
        )


    async def handle_feed_error(
        self,
        error,
    ):

        self.error = (
            f"{type(error).__name__}: {error}"
        )


        print(
            "❌ LIVE FEED ERROR:",
            self.error,
        )


        self.latest = {
            "ts": time.time(),
            "mode": settings.app_mode,

            "status": "LIVE_FEED_ERROR",
            "live": False,

            "prices": {},

            "analysis": {},

            "brains": self.last_live_brains,

            "forecast": {},
            "combined": None,

            "news_score": self.news.score(),
            "news": self.news.latest(),

            "alerts": list(
                self.alerts
            ),

            "error": self.error,

            "market_message": None,
            "last_live_timestamp": None,

            "experimental": True,
        }


        await self.broadcast(
            self.latest
        )


    def build_live_snapshot(
        self,
        prices,
        now,
    ):

        analyses = {
            symbol: analyze(
                symbol,
                self.engine.series(
                    symbol,
                    60,
                ),
            )
            for symbol in (
                "NIFTY",
                "SENSEX",
            )
        }
        price_action = {

            symbol: self.price_action_brain.analyze(
                symbol=symbol,

                candles={
                    "1m": self.engine.series(
                        symbol,
                        60,
                    ),

                    "2m": self.engine.series(
                        symbol,
                        120,
                    ),

                    "3m": self.engine.series(
                        symbol,
                        180,
                    ),

                    "5m": self.engine.series(
                        symbol,
                        300,
                    ),
                },
            )
            for symbol in (
                "NIFTY",
                "SENSEX",
            )
        }
        trade_decisions = {}
        # ADD THE PRINT HERE
        print(
            "🧠 PRICE ACTION |",
            "NIFTY:",
            price_action["NIFTY"]["direction"],
            price_action["NIFTY"]["confidence"],
            "| SENSEX:",
            price_action["SENSEX"]["direction"],
            price_action["SENSEX"]["confidence"],
        )

        news_score = self.news.score()

        forecasts = {}


        for symbol in analyses:

            peer_symbol = (
                "SENSEX"
                if symbol == "NIFTY"
                else "NIFTY"
            )

            peer = analyses[
                peer_symbol
            ]
            analysis = analyses[symbol]

            ctx = DecisionContext(

                symbol=symbol,
                price=prices[symbol],
                support=analysis.get("support"),
                resistance=analysis.get("resistance"),
                atr=analysis.get("atr", 10),
                price_action=price_action[symbol],
                timestamp=now,

            )

            trade_decisions[symbol] = (

                trade_decision_engine

                .decide(ctx)

                .to_dict()

            )

            forecasts[symbol] = [
                predict(
                    analyses[symbol],
                    peer,
                    news_score,
                    horizon,
                )
                for horizon in (
                    3,
                    5,
                    10,
                )
            ]

            # Phase 3: if a trained ML model exists for this
            # symbol+horizon, attach its prediction alongside the V1
            # heuristic (does NOT replace it -- purely additive so you
            # can compare both before switching over).
            ml_forecasts = []

            for horizon in (3, 5, 10):
                ml_result = predict_ml(
                    symbol,
                    horizon,
                    analyses[symbol],
                    peer,
                    news_score,
                )

                if ml_result is not None:
                    ml_forecasts.append(ml_result)

            if ml_forecasts:
                forecasts[f"{symbol}_ML"] = ml_forecasts
        market_time = datetime.fromtimestamp(now)
        live_market = {
            symbol: LiveMarketBrain.analyze(
                now=market_time,
                candles=self.engine.series(symbol, 180),
            )
            for symbol in ("NIFTY", "SENSEX")
        }

        self.live_market_analysis = live_market

        # =====================================================
        # GLOBAL MARKET BRAIN
        # =====================================================

        global_market = GlobalMarketBrain.analyze(

            gift_previous_close=25000,
            gift_current_price=25120,

            dow_change=0.82,
            nasdaq_change=1.10,
            sp500_change=0.71,

            nikkei_change=0.55,
            hang_seng_change=0.40,
            shanghai_change=0.22,

            india_vix=15.5,

            usd_inr=83.20,

            gold_change=-0.80,
            crude_change=-1.10,

        )
        global_market = self.to_json(global_market)

        # BUGFIX: LiveMarketAnalysis is a @dataclass, not a dict --
        # json.dumps()/websocket.send_json() cannot serialize it
        # directly. This was silently killing every websocket
        # broadcast (caught in broadcast()'s except block, which then
        # discarded the client), which is why the dashboard always
        # showed "Clients: 0" after the very first failed send.
        live_market_serializable = self.to_json(live_market)

        self.last_live_brains = {
            "price_action": price_action,
            "live_market": live_market_serializable,
            "global_market": global_market,
            "decision": trade_decisions,
        }

        # print("\n==============================")
        # print("LIVE MARKET BRAIN")
        # print("==============================")
        #
        # for symbol, analysis in live_market.items():
        #     print(f"\n{symbol}")
        #
        #     print("State       :", analysis.market_state)
        #     print("Score       :", analysis.market_score)
        #     print("Trend       :", analysis.trend)
        #     print("Volatility  :", analysis.volatility)
        #     print("Liquidity   :", analysis.liquidity)
        #     print("Strategy    :", analysis.recommended_strategy)
        #
        # print("\n==============================")
        # print("GLOBAL MARKET BRAIN")
        # print("==============================")
        #
        # print("Sentiment   :", global_market["overall_sentiment"])
        # print("Bias        :", global_market["market_bias"])
        # print("Score       :", global_market["market_score"])
        # print("Confidence  :", global_market["confidence"])
        # print("Agreement   :", global_market["agreement"])
        return {
            "ts": now,
            "mode": settings.app_mode,

            "status": "LIVE",
            "live": True,

            "prices": prices,

            "analysis": analyses,

            # "analysis": {},



            "brains": {

                "price_action": price_action,

                "live_market": live_market_serializable,

                "global_market": global_market,

                "decision": trade_decisions,

            },

            # "forecast": {},

            "forecast": forecasts,

            "combined": combined_verdict(
                analyses["NIFTY"],
                analyses["SENSEX"],
            ),

            # Adaptive Confidence Engine -- reweights every brain by
            # its OWN real recent accuracy + current regime, and logs
            # each brain's call so that accuracy can be measured going
            # forward. Additive: your existing "combined" verdict
            # above is untouched.
            "adaptive": {
                symbol: self.compute_adaptive_verdict(
                    symbol, analyses[symbol], price_action, forecasts, now, prices,
                )
                for symbol in ("NIFTY", "SENSEX")
            },

            "options": self.options_analysis,

            "news_score": news_score,
            "news": self.news.latest(),

            "alerts": list(
                self.alerts
            ),

            "error": None,

            "market_message": None,
            "last_live_timestamp": now,

            "experimental": True,
        }


    def store_predictions(
        self,
        now,
    ):

        if not self.latest:
            return


        if not self.latest.get(
            "live",
            False,
        ):

            return


        for symbol, predictions in (
            self.latest["forecast"].items()
        ):

            # Snapshot the market features that were true AT THE MOMENT
            # of this prediction. This is what a future ML model will
            # train on -- without it, the "correct/incorrect" label in
            # the DB has no context to learn from.
            symbol_analysis = self.latest.get(
                "analysis", {}
            ).get(symbol, {})

            peer_symbol = "SENSEX" if symbol == "NIFTY" else "NIFTY"

            peer_analysis = self.latest.get(
                "analysis", {}
            ).get(peer_symbol, {})

            feature_snapshot = {
                "rsi": symbol_analysis.get("rsi"),
                "ema_fast": symbol_analysis.get("ema_fast"),
                "ema_slow": symbol_analysis.get("ema_slow"),
                "atr": symbol_analysis.get("atr"),
                "momentum": symbol_analysis.get("momentum"),
                "state": symbol_analysis.get("state"),
                "regime": symbol_analysis.get("regime"),
                "breakout": symbol_analysis.get("breakout"),
                "support": symbol_analysis.get("support"),
                "resistance": symbol_analysis.get("resistance"),
                "peer_state": peer_analysis.get("state"),
                "news_score": self.latest.get("news_score"),
            }

            for prediction in predictions:

                self.db.add_prediction(
                    now,
                    symbol,
                    prediction["horizon"],
                    self.latest[
                        "prices"
                    ][symbol],
                    prediction,
                    features=feature_snapshot,
                )


    def detect_alert(
        self,
        now,
    ):

        if not self.latest:
            return


        if not self.latest.get(
            "live",
            False,
        ):

            return

        combined = self.latest.get(
            "combined"
        )


        if not combined:
            return


        key = (
            combined["verdict"],
            combined["confirmation"],
        )


        if (
            key != self.last_alert_key
            and combined["verdict"]
            != "NO-TRADE"
        ):

            self.alerts.appendleft(
                {
                    "ts": now,

                    "title": (
                        f'{combined["verdict"]} '
                        "confirmation"
                    ),

                    "message": (
                        "NIFTY and SENSEX are "
                        f'{combined["confirmation"].lower()}. '
                        "Experimental market analysis only."
                    ),
                }
            )

        self.last_alert_key = key

    async def broadcast(
            self,
            payload,
    ):

        print("📡 BROADCAST CALLED")
        print("Clients:", len(self.clients))

        dead_clients = []

        for websocket in self.clients:
            try:
                print("➡ Sending data to client...")
                await websocket.send_json(payload)
                print("✅ Sent successfully")

            except Exception as e:
                print("❌ Send failed:", e)
                dead_clients.append(websocket)

        for websocket in dead_clients:
            self.clients.discard(websocket)

    @staticmethod
    def to_json(obj):
        """
        Convert dataclasses, Enums, dicts and lists into
        JSON-serializable objects.
        """

        if is_dataclass(obj):
            obj = asdict(obj)

        if isinstance(obj, Enum):
            return obj.value

        if isinstance(obj, dict):
            return {
                k: MarketService.to_json(v)
                for k, v in obj.items()
            }

        if isinstance(obj, (list, tuple)):
            return [
                MarketService.to_json(v)
                for v in obj
            ]

        return obj


service = MarketService()