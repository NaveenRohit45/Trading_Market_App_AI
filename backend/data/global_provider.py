"""
============================================================
Trading Market AI
Global Market Provider V1
============================================================

Provides:

✓ GIFT Nifty
✓ US Markets
✓ Asian Markets
✓ India VIX
✓ USD/INR
✓ Gold
✓ Crude Oil

Author : Super Cat
"""

from __future__ import annotations

import requests

from backend.config import settings


class GlobalProvider:

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self):

        if not settings.finnhub_api_key:
            raise RuntimeError(
                "FINNHUB_API_KEY missing in .env"
            )

        self.api_key = settings.finnhub_api_key

    # --------------------------------------------------------
    # Common GET
    # --------------------------------------------------------

    def _get(self, endpoint, **params):

        params["token"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------------
    # Quote
    # --------------------------------------------------------

    def quote(self, symbol):

        return self._get(
            "quote",
            symbol=symbol,
        )

    # --------------------------------------------------------
    # Forex
    # --------------------------------------------------------

    def forex(self, symbol):

        return self.quote(symbol)

    # --------------------------------------------------------
    # Index
    # --------------------------------------------------------

    def index(self, symbol):

        return self.quote(symbol)

    # --------------------------------------------------------
    # Commodity
    # --------------------------------------------------------

    def commodity(self, symbol):

        return self.quote(symbol)

    # --------------------------------------------------------
    # GIFT Nifty
    # --------------------------------------------------------

    def gift_nifty(self):

        return self.quote("^NSEI")

    # --------------------------------------------------------
    # US
    # --------------------------------------------------------

    def us_markets(self):

        return {

            "dow": self.quote("DJI"),

            "nasdaq": self.quote("IXIC"),

            "sp500": self.quote("SPX"),

        }

    # --------------------------------------------------------
    # Asia
    # --------------------------------------------------------

    def asian_markets(self):

        return {

            "nikkei": self.quote("N225"),

            "hang_seng": self.quote("HSI"),

            "shanghai": self.quote("000001.SS"),

        }

    # --------------------------------------------------------
    # VIX
    # --------------------------------------------------------

    def india_vix(self):

        return self.quote("^VIX")

    # --------------------------------------------------------
    # USD INR
    # --------------------------------------------------------

    def usd_inr(self):

        return self.forex("OANDA:USD_INR")

    # --------------------------------------------------------
    # Commodities
    # --------------------------------------------------------

    def commodities(self):

        return {

            "gold": self.quote("XAUUSD"),

            "crude": self.quote("USOIL"),

        }


global_provider = GlobalProvider()