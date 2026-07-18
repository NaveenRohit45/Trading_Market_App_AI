import asyncio
import json
import time
from pathlib import Path

from growwapi import GrowwAPI, GrowwFeed

from backend.config import settings
from backend.models import Candle


class GrowwProvider:

    def __init__(self):

        if not settings.groww_api_key:
            raise RuntimeError(
                "GROWW_API_KEY is missing from .env"
            )

        if not settings.groww_api_secret:
            raise RuntimeError(
                "GROWW_API_SECRET is missing from .env"
            )

        print("=" * 60)
        print("CONNECTING TO GROWW")
        print("=" * 60)

        access_token = GrowwAPI.get_access_token(
            api_key=settings.groww_api_key,
            secret=settings.groww_api_secret,
        )

        self.groww = GrowwAPI(access_token)

        print("✅ Connected to Groww")

        self.feed = GrowwFeed(self.groww)
        self.subscribed = False

        self.instruments = [
            {
                "exchange": "NSE",
                "segment": "CASH",
                "exchange_token": "NIFTY",
            },
            {
                "exchange": "BSE",
                "segment": "CASH",
                "exchange_token": "1",
            },
        ]

        # Persistent last genuine live snapshot.
        # Works on both Windows and Mac.
        self.cache_file = (
            Path(__file__).resolve().parent
            / "groww_last_snapshot.json"
        )


    async def start(self):
        pass


    def get_historical_candles(self, symbol, interval_minutes=1, days_back=5):
        """
        Fetch historical candles directly from Groww (no Yahoo Finance).
        Returns a list of dicts: {start_ts, open, high, low, close, volume}
        sorted oldest -> newest, or [] on any failure.
        """

        from datetime import datetime, timedelta

        # Per Groww's official docs (groww.in/trade-api/docs/curl/backtesting):
        # "Groww symbol is formed by concatenating exchange and trading
        # symbol. For Stocks and Indices: Only exchange and trading
        # symbol are used." e.g. NSE-WIPRO, NOT bare "WIPRO".
        # Passing the bare symbol was the actual cause of the earlier
        # "Access forbidden" error, not a subscription/permission issue.
        symbol_map = {
            "NIFTY": {"exchange": "NSE", "segment": "CASH", "groww_symbol": "NSE-NIFTY"},
            "SENSEX": {"exchange": "BSE", "segment": "CASH", "groww_symbol": "BSE-SENSEX"},
        }

        if symbol not in symbol_map:
            print(f"⚠️ No Groww symbol mapping for {symbol}")
            return []

        cfg = symbol_map[symbol]

        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        interval_str = f"{interval_minutes}minute"

        try:
            response = self.groww.get_historical_candles(
                exchange=cfg["exchange"],
                segment=cfg["segment"],
                groww_symbol=cfg["groww_symbol"],
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                candle_interval=interval_str,
            )
        except Exception as error:
            print(f"⚠️ Groww historical fetch failed for {symbol}: {error}")
            return []

        raw_candles = response.get("candles", []) if isinstance(response, dict) else []

        if not raw_candles:
            print(f"⚠️ Groww returned no historical candles for {symbol}")
            return []

        candles = []

        for row in raw_candles:
            try:
                ts, o, h, l, c = row[0], row[1], row[2], row[3], row[4]
                vol = row[5] if len(row) > 5 else 0.0

                ts = float(ts)
                if ts > 10_000_000_000:
                    ts = ts / 1000.0

                candles.append(Candle(
                    symbol=symbol,
                    start_ts=ts,
                    open=float(o),
                    high=float(h),
                    low=float(l),
                    close=float(c),
                    volume=float(vol),
                ))
            except (IndexError, TypeError, ValueError):
                continue

        candles.sort(key=lambda x: x.start_ts)

        print(f"✅ Groww historical: {len(candles)} x {interval_minutes}m candles for {symbol}")

        return candles


    async def stop(self):

        print(
            "🛑 Groww market data provider stopped"
        )


    def save_live_snapshot(
        self,
        nifty_price,
        sensex_price,
    ):

        snapshot = {
            "timestamp": time.time(),
            "prices": {
                "NIFTY": nifty_price,
                "SENSEX": sensex_price,
            },
        }

        self.cache_file.write_text(
            json.dumps(
                snapshot,
                indent=2,
            ),
            encoding="utf-8",
        )


    def load_last_snapshot(self):

        if not self.cache_file.exists():
            return None

        try:

            data = json.loads(
                self.cache_file.read_text(
                    encoding="utf-8"
                )
            )

            prices = data.get(
                "prices",
                {}
            )

            nifty_price = float(
                prices["NIFTY"]
            )

            sensex_price = float(
                prices["SENSEX"]
            )

            if (
                nifty_price <= 0
                or sensex_price <= 0
            ):
                return None

            return {
                "status": "MARKET_CLOSED",
                "live": False,
                "timestamp": data.get(
                    "timestamp"
                ),
                "prices": {
                    "NIFTY": nifty_price,
                    "SENSEX": sensex_price,
                },
            }

        except Exception as error:

            print(
                "⚠️ Could not load last Groww snapshot:",
                error,
            )

            return None


    async def get_prices(self):

        # --------------------------------------------------
        # SUBSCRIBE ONLY ONCE
        # --------------------------------------------------

        if not self.subscribed:

            print(
                "📡 Subscribing to NIFTY + SENSEX index stream..."
            )

            result = await asyncio.to_thread(
                self.feed.subscribe_index_value,
                self.instruments,
            )

            print(
                "✅ Groww index subscription:",
                result,
            )

            self.subscribed = True

            await asyncio.sleep(1)


        # --------------------------------------------------
        # READ CURRENT STREAM VALUES
        # --------------------------------------------------

        data = await asyncio.to_thread(
            self.feed.get_index_value
        )

        try:

            nifty_data = (
                data["NSE"]["CASH"]["NIFTY"]
            )

            sensex_data = (
                data["BSE"]["CASH"]["1"]
            )

        except (
            KeyError,
            TypeError,
        ) as error:

            raise RuntimeError(
                f"Invalid Groww index stream structure: {data}"
            ) from error


        # --------------------------------------------------
        # CONNECTED, BUT NO CURRENT TICKS
        # --------------------------------------------------

        if (
            nifty_data is None
            or sensex_data is None
        ):

            cached = self.load_last_snapshot()

            if cached:

                print(
                    "🌙 MARKET CLOSED | "
                    f'NIFTY: {cached["prices"]["NIFTY"]} | '
                    f'SENSEX: {cached["prices"]["SENSEX"]}'
                )

                return cached

            print(
                "🌙 MARKET CLOSED | "
                "No saved closing snapshot available yet"
            )

            return {
                "status": "MARKET_CLOSED",
                "live": False,
                "timestamp": None,
                "prices": {},
            }


        # --------------------------------------------------
        # REAL LIVE VALUES
        # --------------------------------------------------

        try:

            nifty_price = float(
                nifty_data["value"]
            )

            sensex_price = float(
                sensex_data["value"]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:

            raise RuntimeError(
                f"Invalid Groww index values: {data}"
            ) from error


        if nifty_price <= 0:
            raise RuntimeError(
                "Invalid NIFTY stream value"
            )

        if sensex_price <= 0:
            raise RuntimeError(
                "Invalid SENSEX stream value"
            )


        # Save only genuine live values.
        self.save_live_snapshot(
            nifty_price,
            sensex_price,
        )


        return {
            "status": "LIVE",
            "live": True,
            "timestamp": time.time(),
            "prices": {
                "NIFTY": nifty_price,
                "SENSEX": sensex_price,
            },
        }