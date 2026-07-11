"""
option_chain.py

Trading Market AI
Options Brain V2

Responsibilities
----------------
• Normalize Option Chain
• Fast strike lookup
• Cached statistics
• ATM calculations
• Validation
• Common helper functions

NOTE:
This module contains NO trading logic.
It is only a data model used by all analyzers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================
# Option Data
# ============================================================

@dataclass(slots=True)
class OptionData:
    """
    Represents one option strike.
    """

    strike: float

    call_ltp: float
    put_ltp: float

    call_oi: int
    put_oi: int

    call_change_oi: int
    put_change_oi: int

    call_iv: float
    put_iv: float

    call_volume: int
    put_volume: int


# ============================================================
# Option Chain
# ============================================================

class OptionChain:

    def __init__(
        self,
        symbol: str,
        expiry: str,
        spot_price: float,
        options: List[OptionData],
    ):

        self.symbol = symbol.upper()

        self.expiry = expiry

        self.spot_price = float(spot_price)

        self.options = sorted(
            options,
            key=lambda x: x.strike
        )

        # ------------------------------------------
        # Validation
        # ------------------------------------------

        self._validate()

        # ------------------------------------------
        # Cached lookup dictionary
        # strike -> OptionData
        # ------------------------------------------

        self._strike_map: Dict[float, OptionData] = {

            option.strike: option

            for option in self.options

        }

        # ------------------------------------------
        # Cached strike list
        # ------------------------------------------

        self._strikes = list(
            self._strike_map.keys()
        )

        # ------------------------------------------
        # Cached Statistics
        # (filled automatically)
        # ------------------------------------------

        self._cache_statistics()

    # ========================================================
    # Validation
    # ========================================================

    def _validate(self):

        if not self.options:

            raise ValueError(
                "OptionChain contains no strikes."
            )

        strikes = set()

        for option in self.options:

            if option.strike in strikes:

                raise ValueError(
                    f"Duplicate strike found: {option.strike}"
                )

            strikes.add(option.strike)

        for option in self.options:

            if option.strike <= 0:
                raise ValueError(
                    f"Invalid strike: {option.strike}"
                )

            if option.call_ltp < 0:
                raise ValueError(
                    "Negative Call LTP not allowed."
                )

            if option.put_ltp < 0:
                raise ValueError(
                    "Negative Put LTP not allowed."
                )

            if option.call_oi < 0:
                raise ValueError(
                    "Negative Call OI not allowed."
                )

            if option.put_oi < 0:
                raise ValueError(
                    "Negative Put OI not allowed."
                )

            if option.call_change_oi < 0:
                raise ValueError(
                    "Negative Call Change OI not allowed."
                )

            if option.put_change_oi < 0:
                raise ValueError(
                    "Negative Put Change OI not allowed."
                )

            if option.call_iv < 0:
                raise ValueError(
                    "Negative Call IV not allowed."
                )

            if option.put_iv < 0:
                raise ValueError(
                    "Negative Put IV not allowed."
                )

            if option.call_volume < 0:
                raise ValueError(
                    "Negative Call Volume not allowed."
                )

            if option.put_volume < 0:
                raise ValueError(
                    "Negative Put Volume not allowed."
                )

    # ========================================================
    # Cache
    # ========================================================

    def _cache_statistics(self):

        self.total_call_oi = 0
        self.total_put_oi = 0

        self.total_call_volume = 0
        self.total_put_volume = 0

        self.total_call_premium = 0.0
        self.total_put_premium = 0.0

        self.call_iv_sum = 0.0
        self.put_iv_sum = 0.0

        self.call_iv_count = 0
        self.put_iv_count = 0

        # ----------------------------------------

        for option in self.options:

            self.total_call_oi += option.call_oi
            self.total_put_oi += option.put_oi

            self.total_call_volume += option.call_volume
            self.total_put_volume += option.put_volume

            self.total_call_premium += (
                option.call_ltp *
                option.call_volume
            )

            self.total_put_premium += (
                option.put_ltp *
                option.put_volume
            )

            if option.call_iv > 0:

                self.call_iv_sum += option.call_iv
                self.call_iv_count += 1

            if option.put_iv > 0:

                self.put_iv_sum += option.put_iv
                self.put_iv_count += 1

        # ----------------------------------------

        self.average_call_iv = (

            self.call_iv_sum /
            self.call_iv_count

            if self.call_iv_count

            else 0.0

        )

        self.average_put_iv = (

            self.put_iv_sum /
            self.put_iv_count

            if self.put_iv_count

            else 0.0

        )

    # ========================================================
    # Basic Properties
    # ========================================================

    @property
    def strike_count(self) -> int:

        return len(self.options)

    @property
    def strikes(self) -> List[float]:

        return self._strikes.copy()

    # ========================================================
    # Fast Lookup
    # ========================================================

    def has_strike(
        self,
        strike: float
    ) -> bool:

        return strike in self._strike_map

    def get_strike(
        self,
        strike: float
    ) -> Optional[OptionData]:

        return self._strike_map.get(
            strike
        )

    # ========================================================
    # ATM / Strike Navigation
    # ========================================================

    def get_atm_strike(self) -> float:
        """
        Returns the strike nearest to the current spot price.
        """

        return min(
            self._strikes,
            key=lambda strike: abs(strike - self.spot_price)
        )

    # --------------------------------------------------------

    def get_nearest_strike(
        self,
        price: float
    ) -> float:
        """
        Returns strike nearest to any given price.
        """

        return min(
            self._strikes,
            key=lambda strike: abs(strike - price)
        )

    # --------------------------------------------------------

    def get_previous_strike(
        self,
        strike: float
    ) -> Optional[float]:
        """
        Returns previous available strike.
        """

        if strike not in self._strike_map:
            strike = self.get_nearest_strike(strike)

        index = self._strikes.index(strike)

        if index == 0:
            return None

        return self._strikes[index - 1]

    # --------------------------------------------------------

    def get_next_strike(
        self,
        strike: float
    ) -> Optional[float]:
        """
        Returns next available strike.
        """

        if strike not in self._strike_map:
            strike = self.get_nearest_strike(strike)

        index = self._strikes.index(strike)

        if index == len(self._strikes) - 1:
            return None

        return self._strikes[index + 1]

    # ========================================================
    # ITM / OTM Helpers
    # ========================================================

    def get_itm_call_strikes(self) -> List[float]:
        """
        ITM Call strikes are below spot.
        """

        return [
            strike
            for strike in self._strikes
            if strike < self.spot_price
        ]

    # --------------------------------------------------------

    def get_otm_call_strikes(self) -> List[float]:
        """
        OTM Call strikes are above spot.
        """

        return [
            strike
            for strike in self._strikes
            if strike > self.spot_price
        ]

    # --------------------------------------------------------

    def get_itm_put_strikes(self) -> List[float]:
        """
        ITM Put strikes are above spot.
        """

        return [
            strike
            for strike in self._strikes
            if strike > self.spot_price
        ]

    # --------------------------------------------------------

    def get_otm_put_strikes(self) -> List[float]:
        """
        OTM Put strikes are below spot.
        """

        return [
            strike
            for strike in self._strikes
            if strike < self.spot_price
        ]

    # ========================================================
    # Range Helpers
    # ========================================================

    def get_strikes_between(
        self,
        lower: float,
        upper: float
    ) -> List[OptionData]:
        """
        Returns OptionData objects inside a strike range.
        """

        return [

            option

            for option in self.options

            if lower <= option.strike <= upper

        ]

    # --------------------------------------------------------

    def get_strikes_above(
        self,
        strike: float
    ) -> List[OptionData]:

        return [

            option

            for option in self.options

            if option.strike > strike

        ]

    # --------------------------------------------------------

    def get_strikes_below(
        self,
        strike: float
    ) -> List[OptionData]:

        return [

            option

            for option in self.options

            if option.strike < strike

        ]

    # ========================================================
    # ATM Helpers
    # ========================================================

    def get_atm_option(self) -> OptionData:
        """
        Returns OptionData for ATM strike.
        """

        return self.get_strike(
            self.get_atm_strike()
        )

    # --------------------------------------------------------

    def get_itm_call_options(self) -> List[OptionData]:

        return [
            self._strike_map[s]
            for s in self.get_itm_call_strikes()
        ]

    # --------------------------------------------------------

    def get_otm_call_options(self) -> List[OptionData]:

        return [
            self._strike_map[s]
            for s in self.get_otm_call_strikes()
        ]

    # --------------------------------------------------------

    def get_itm_put_options(self) -> List[OptionData]:

        return [
            self._strike_map[s]
            for s in self.get_itm_put_strikes()
        ]

    # --------------------------------------------------------

    def get_otm_put_options(self) -> List[OptionData]:

        return [
            self._strike_map[s]
            for s in self.get_otm_put_strikes()
        ]

    # ========================================================
    # Cached Statistics Getters
    # ========================================================

    def get_total_call_oi(self) -> int:
        return self.total_call_oi

    # --------------------------------------------------------

    def get_total_put_oi(self) -> int:
        return self.total_put_oi

    # --------------------------------------------------------

    def get_total_call_volume(self) -> int:
        return self.total_call_volume

    # --------------------------------------------------------

    def get_total_put_volume(self) -> int:
        return self.total_put_volume

    # --------------------------------------------------------

    def get_total_call_premium(self) -> float:
        return self.total_call_premium

    # --------------------------------------------------------

    def get_total_put_premium(self) -> float:
        return self.total_put_premium

    # --------------------------------------------------------

    def get_average_call_iv(self) -> float:
        return round(self.average_call_iv, 2)

    # --------------------------------------------------------

    def get_average_put_iv(self) -> float:
        return round(self.average_put_iv, 2)

    # ========================================================
    # Dictionary Helpers
    # ========================================================

    def get_call_oi(self) -> Dict[float, int]:

        return {
            option.strike: option.call_oi
            for option in self.options
        }

    # --------------------------------------------------------

    def get_put_oi(self) -> Dict[float, int]:

        return {
            option.strike: option.put_oi
            for option in self.options
        }

    # --------------------------------------------------------

    def get_call_change_oi(self) -> Dict[float, int]:

        return {
            option.strike: option.call_change_oi
            for option in self.options
        }

    # --------------------------------------------------------

    def get_put_change_oi(self) -> Dict[float, int]:

        return {
            option.strike: option.put_change_oi
            for option in self.options
        }

    # --------------------------------------------------------

    def get_call_iv(self) -> Dict[float, float]:

        return {
            option.strike: option.call_iv
            for option in self.options
        }

    # --------------------------------------------------------

    def get_put_iv(self) -> Dict[float, float]:

        return {
            option.strike: option.put_iv
            for option in self.options
        }

    # --------------------------------------------------------

    def get_call_volume(self) -> Dict[float, int]:

        return {
            option.strike: option.call_volume
            for option in self.options
        }

    # --------------------------------------------------------

    def get_put_volume(self) -> Dict[float, int]:

        return {
            option.strike: option.put_volume
            for option in self.options
        }

    # ========================================================
    # Summary
    # ========================================================

    def summary(self) -> Dict:

        atm = self.get_atm_strike()

        return {

            "symbol": self.symbol,

            "expiry": self.expiry,

            "spot_price": self.spot_price,

            "atm_strike": atm,

            "strike_count": self.strike_count,

            "total_call_oi": self.total_call_oi,

            "total_put_oi": self.total_put_oi,

            "total_call_volume": self.total_call_volume,

            "total_put_volume": self.total_put_volume,

            "average_call_iv": round(
                self.average_call_iv,
                2
            ),

            "average_put_iv": round(
                self.average_put_iv,
                2
            )

        }

    # ========================================================
    # Export
    # ========================================================

    def to_dict(self) -> Dict:

        return {

            "symbol": self.symbol,

            "expiry": self.expiry,

            "spot_price": self.spot_price,

            "options": [

                {

                    "strike": option.strike,

                    "call_ltp": option.call_ltp,

                    "put_ltp": option.put_ltp,

                    "call_oi": option.call_oi,

                    "put_oi": option.put_oi,

                    "call_change_oi": option.call_change_oi,

                    "put_change_oi": option.put_change_oi,

                    "call_iv": option.call_iv,

                    "put_iv": option.put_iv,

                    "call_volume": option.call_volume,

                    "put_volume": option.put_volume,

                }

                for option in self.options

            ]

        }

    # ========================================================
    # Magic Methods
    # ========================================================

    def __len__(self):

        return len(self.options)

    # --------------------------------------------------------

    def __contains__(
        self,
        strike: float
    ):

        return strike in self._strike_map

    # --------------------------------------------------------

    def __getitem__(
        self,
        strike: float
    ) -> OptionData:

        return self._strike_map[strike]

    # --------------------------------------------------------

    def __iter__(self):

        return iter(self.options)

    # --------------------------------------------------------

    def __repr__(self):

        return (

            f"OptionChain("
            f"symbol={self.symbol}, "
            f"spot={self.spot_price}, "
            f"expiry='{self.expiry}', "
            f"strikes={self.strike_count})"

        )