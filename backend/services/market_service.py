
import asyncio
import time
from collections import deque

from backend.config import settings
from backend.core.candle_engine import CandleEngine
from backend.analyzers.market_analyzer import analyze
from backend.analyzers.news_analyzer import NewsAnalyzer
from backend.prediction.prediction_engine import predict, combined_verdict
from backend.services.database import Database
from backend.data.demo_provider import DemoProvider
from backend.data.groww_provider import GrowwProvider


class MarketService:

    def __init__(self):

        self.provider = (
            GrowwProvider()
            if settings.app_mode == "GROWW"
            else DemoProvider()
        )

        self.engine = CandleEngine()
        self.news = NewsAnalyzer()
        self.db = Database(settings.db_path)

        self.clients = set()

        # IMPORTANT:
        # Never preload or preserve old/demo market data.
        self.latest = {}

        self.last_prediction = 0
        self.last_alert_key = None

        self.running = False
        self.error = None

        self.alerts = deque(maxlen=20)

        self.loop_task = None


    async def start(self):

        print("=" * 60)
        print("STARTING ADA MARKET SERVICE")
        print(f"MODE: {settings.app_mode}")
        print("=" * 60)

        self.running = True

        # Start the background loop first.
        # Groww live-feed failure must NOT kill FastAPI startup.
        self.loop_task = asyncio.create_task(
            self.loop()
        )

        print("✅ Market service background loop started")


    async def stop(self):

        print("Stopping ADA Market Service...")

        self.running = False

        if self.loop_task:

            self.loop_task.cancel()

            try:
                await self.loop_task

            except asyncio.CancelledError:
                pass

        await self.provider.stop()

        print("🛑 ADA Market Service stopped")


    async def loop(self):

        while self.running:

            try:

                now = time.time()

                # --------------------------------------------------
                # GET REAL MARKET PRICES
                # --------------------------------------------------

                prices = await self.provider.get_prices()

                # --------------------------------------------------
                # VALIDATE LIVE SNAPSHOT
                # --------------------------------------------------

                if not isinstance(prices, dict):

                    raise RuntimeError(
                        "Live provider returned invalid price data"
                    )

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

                for symbol, price in prices.items():

                    self.engine.add_tick(
                        symbol,
                        price,
                        now,
                        60,
                    )

                self.db.resolve(
                    now,
                    prices,
                )

                self.latest = self.build_snapshot(
                    prices,
                    now,
                )

                if (
                    now - self.last_prediction
                    >= settings.prediction_interval_seconds
                ):

                    self.store_predictions(now)

                    self.last_prediction = now

                self.detect_alert(now)

                await self.broadcast(
                    self.latest
                )

                print(
                    "📡 LIVE GROWW SNAPSHOT | "
                    f"NIFTY: {nifty_price} | "
                    f"SENSEX: {sensex_price}"
                )


            except asyncio.CancelledError:

                raise


            except Exception as error:

                self.error = (
                    f"{type(error).__name__}: {error}"
                )

                print(
                    "❌ LIVE FEED ERROR:",
                    self.error,
                )

                # IMPORTANT:
                # Destroy stale snapshot immediately.
                # Never leave old DEMO/live prices visible.
                self.latest = {
                    "ts": time.time(),
                    "mode": settings.app_mode,
                    "status": "LIVE_FEED_ERROR",
                    "live": False,
                    "prices": {},
                    "analysis": {},
                    "forecast": {},
                    "combined": None,
                    "news_score": self.news.score(),
                    "news": self.news.latest(),
                    "alerts": list(self.alerts),
                    "error": self.error,
                    "experimental": True,
                }

                # Tell every connected dashboard immediately.
                await self.broadcast(
                    self.latest
                )


            await asyncio.sleep(
                settings.poll_seconds
            )


    def build_snapshot(
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

        return {
            "ts": now,
            "mode": settings.app_mode,
            "status": "LIVE",
            "live": True,
            "prices": prices,
            "analysis": analyses,
            "forecast": forecasts,
            "combined": combined_verdict(
                analyses["NIFTY"],
                analyses["SENSEX"],
            ),
            "news_score": news_score,
            "news": self.news.latest(),
            "alerts": list(self.alerts),
            "error": None,
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

            for prediction in predictions:

                self.db.add_prediction(
                    now,
                    symbol,
                    prediction["horizon"],
                    self.latest[
                        "prices"
                    ][symbol],
                    prediction,
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

        dead_clients = []

        for websocket in self.clients:

            try:

                await websocket.send_json(
                    payload
                )

            except Exception:

                dead_clients.append(
                    websocket
                )

        for websocket in dead_clients:

            self.clients.discard(
                websocket
            )


service = MarketService()

