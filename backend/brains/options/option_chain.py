"""
option_chain.py

Options Chain Normalizer

Responsibilities:
- Store normalized option chain
- Extract ATM strike
- Provide helper methods for analyzers

No trading logic should exist here.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class OptionData:
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


class OptionChain:

    def __init__(
        self,
        symbol: str,
        expiry: str,
        spot_price: float,
        options: List[OptionData],
    ):
        self.symbol = symbol
        self.expiry = expiry
        self.spot_price = spot_price
        self.options = sorted(options, key=lambda x: x.strike)

    # ---------------------------------------------------------

    def get_atm_strike(self) -> float:
        """
        Returns nearest ATM strike.
        """

        return min(
            self.options,
            key=lambda x: abs(x.strike - self.spot_price)
        ).strike

    # ---------------------------------------------------------

    def get_strike(self, strike: float) -> Optional[OptionData]:

        for option in self.options:
            if option.strike == strike:
                return option

        return None

    # ---------------------------------------------------------

    def get_all_strikes(self) -> List[float]:

        return [o.strike for o in self.options]

    # ---------------------------------------------------------

    def get_call_oi(self) -> Dict[float, int]:

        return {
            o.strike: o.call_oi
            for o in self.options
        }

    # ---------------------------------------------------------

    def get_put_oi(self) -> Dict[float, int]:

        return {
            o.strike: o.put_oi
            for o in self.options
        }

    # ---------------------------------------------------------

    def get_call_change_oi(self) -> Dict[float, int]:

        return {
            o.strike: o.call_change_oi
            for o in self.options
        }

    # ---------------------------------------------------------

    def get_put_change_oi(self) -> Dict[float, int]:

        return {
            o.strike: o.put_change_oi
            for o in self.options
        }

    # ---------------------------------------------------------

    def get_call_iv(self) -> Dict[float, float]:

        return {
            o.strike: o.call_iv
            for o in self.options
        }

    # ---------------------------------------------------------

    def get_put_iv(self) -> Dict[float, float]:

        return {
            o.strike: o.put_iv
            for o in self.options
        }

    # ---------------------------------------------------------

    def get_call_volume(self) -> Dict[float, int]:

        return {
            o.strike: o.call_volume
            for o in self.options
        }

    # ---------------------------------------------------------

    def get_put_volume(self) -> Dict[float, int]:

        return {
            o.strike: o.put_volume
            for o in self.options
        }

    # ---------------------------------------------------------

    def to_dict(self):

        return {
            "symbol": self.symbol,
            "expiry": self.expiry,
            "spot_price": self.spot_price,
            "atm_strike": self.get_atm_strike(),
            "total_strikes": len(self.options),
        }