import asyncio

from growwapi import GrowwAPI, GrowwFeed

from backend.config import settings


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


    async def start(self):

        # MarketService currently starts its own polling loop.
        # Subscription is created lazily on first get_prices().
        pass


    async def stop(self):

        print(
            "🛑 Groww market data provider stopped"
        )


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

            # Give the feed a moment to receive first values.
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
                f"Incomplete Groww index stream: {data}"
            ) from error


        if nifty_price <= 0:
            raise RuntimeError(
                "Invalid NIFTY stream value"
            )

        if sensex_price <= 0:
            raise RuntimeError(
                "Invalid SENSEX stream value"
            )


        return {
            "NIFTY": nifty_price,
            "SENSEX": sensex_price,
        }