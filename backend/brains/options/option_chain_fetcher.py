"""
option_chain_fetcher.py

Trading Market AI
Options Brain V3

Responsible for

• Downloading live option chain
• Building OptionChain objects
• Caching
• Validation
• Error handling

This module DOES NOT analyze options.
It only fetches and prepares data.

Author : Super Cat
Version : 3.0
"""

from __future__ import annotations

import time
from typing import Optional

from .option_chain import OptionChain


# ==========================================================
# Configuration
# ==========================================================

CACHE_SECONDS = 3


# ==========================================================
# Fetcher
# ==========================================================

class OptionChainFetcher:

    def __init__(self):

        self._cached_chain: Optional[OptionChain] = None

        self._last_refresh = 0.0

        self._last_error: Optional[str] = None

        self._connected = False

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def get_chain(
        self,
        symbol: str = "NIFTY",
        force_refresh: bool = False,
    ) -> OptionChain:

        if (

            force_refresh

            or

            self._cache_expired()

        ):

            self.refresh(symbol)

        if self._cached_chain is None:

            raise RuntimeError(

                "No option chain available."

            )

        return self._cached_chain

    # ------------------------------------------------------
    # Refresh
    # ------------------------------------------------------

    def refresh(
        self,
        symbol: str,
    ):

        raw = self._download(symbol)

        chain = self._parse(raw)

        self._validate(chain)

        self._cached_chain = chain

        self._last_refresh = time.time()

        self._connected = True

        self._last_error = None

    # ------------------------------------------------------
    # Cache
    # ------------------------------------------------------

    def _cache_expired(self):

        return (

            time.time()

            - self._last_refresh

        ) >= CACHE_SECONDS

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    @property
    def connected(self):

        return self._connected

    @property
    def last_error(self):

        return self._last_error

    @property
    def last_refresh(self):

        return self._last_refresh

    # ======================================================
    # Internal (implemented in Part 2)
    # ======================================================

    # ------------------------------------------------------
    # Download
    # ------------------------------------------------------

    def _download(
            self,
            symbol: str,
    ):

        """
        Downloads raw option-chain data.

        Part 2 uses a provider stub.

        Part 3 will integrate the real
        Groww option-chain provider.
        """

        return {

            "symbol": symbol,

            "spot_price": None,

            "expiry": None,

            "options": []

        }

    # ------------------------------------------------------
    # Parse
    # ------------------------------------------------------

    # ------------------------------------------------------
    # Parse Provider Data
    # ------------------------------------------------------

    def _parse(
            self,
            raw,
    ) -> OptionChain:

        """
        Converts provider data into an OptionChain.

        Expected raw format:

        {
            "symbol": "...",
            "expiry": "...",
            "spot_price": 25120,
            "options": [
                {
                    "strike":25100,
                    "call_ltp":...,
                    ...
                }
            ]
        }
        """

        from .option_chain import (
            OptionChain,
            OptionData,
        )

        symbol = raw.get("symbol")

        expiry = raw.get("expiry")

        spot_price = raw.get("spot_price")

        option_rows = raw.get(
            "options",
            [],
        )

        options = []

        for row in option_rows:
            option = OptionData(

                strike=float(
                    row["strike"]
                ),

                call_ltp=float(
                    row.get(
                        "call_ltp",
                        0,
                    )
                ),

                put_ltp=float(
                    row.get(
                        "put_ltp",
                        0,
                    )
                ),

                call_oi=int(
                    row.get(
                        "call_oi",
                        0,
                    )
                ),

                put_oi=int(
                    row.get(
                        "put_oi",
                        0,
                    )
                ),

                call_change_oi=int(
                    row.get(
                        "call_change_oi",
                        0,
                    )
                ),

                put_change_oi=int(
                    row.get(
                        "put_change_oi",
                        0,
                    )
                ),

                call_iv=float(
                    row.get(
                        "call_iv",
                        0,
                    )
                ),

                put_iv=float(
                    row.get(
                        "put_iv",
                        0,
                    )
                ),

                call_volume=int(
                    row.get(
                        "call_volume",
                        0,
                    )
                ),

                put_volume=int(
                    row.get(
                        "put_volume",
                        0,
                    )
                ),

            )

            options.append(option)

        return OptionChain(

            symbol=symbol,

            expiry=expiry,

            spot_price=spot_price,

            options=options,

        )

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    def _validate(
            self,
            chain: OptionChain,
    ):

        if chain is None:
            raise ValueError(
                "OptionChain is None."
            )

        if not chain.symbol:
            raise ValueError(
                "Missing symbol."
            )

        if chain.spot_price <= 0:
            raise ValueError(
                "Invalid spot price."
            )

        if len(chain.options) == 0:
            raise ValueError(
                "No option data received."
            )

        strikes = set()

        for option in chain.options:

            if option.strike <= 0:
                raise ValueError(
                    f"Invalid strike: {option.strike}"
                )

            if option.strike in strikes:
                raise ValueError(
                    f"Duplicate strike: {option.strike}"
                )

            strikes.add(option.strike)

            if option.call_oi < 0:
                raise ValueError(
                    "Negative Call OI."
                )

            if option.put_oi < 0:
                raise ValueError(
                    "Negative Put OI."
                )

            if option.call_iv < 0:
                raise ValueError(
                    "Negative Call IV."
                )

            if option.put_iv < 0:
                raise ValueError(
                    "Negative Put IV."
                )

            if option.call_volume < 0:
                raise ValueError(
                    "Negative Call Volume."
                )

            if option.put_volume < 0:
                raise ValueError(
                    "Negative Put Volume."
                )


# ==========================================================
# Singleton
# ==========================================================

option_chain_fetcher = OptionChainFetcher()