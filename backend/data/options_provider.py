"""
Options Flow Provider — PCR + Open Interest Shift Signal

This is a genuinely new signal source, not present anywhere else in
the system: options positioning data. Two things computed here that
price/candle data alone cannot give you:

1. Put-Call Ratio (PCR) -- by open interest and by volume. A rising
   PCR (more puts than calls being held/traded) is traditionally read
   as bearish positioning; a falling PCR as bullish. This is a
   CONTRARIAN or CONFIRMING signal depending on regime -- we don't
   hardcode which, we just expose the number and let the Adaptive
   Confidence Engine learn (via its own tracked accuracy) whether
   this brain's calls are actually working, same as every other brain.

2. Open Interest SHIFT -- the change in OI per strike between
   consecutive fetches. Large OI buildup at a specific strike close
   to spot price often marks where big players expect price to
   pin/reverse (relevant to "max pain" theory). A single snapshot
   can't show this -- it requires comparing against the previous
   fetch, which is why this module keeps in-memory previous state.

HONEST LIMITATION: options-based signals are widely used but not
infallible -- PCR extremes can persist through strong trends, and
"max pain" theory is disputed. Treat this exactly like every other
brain here: it casts a vote, and the Adaptive Confidence Engine
tracks whether that vote is actually right often enough to deserve
weight. Nothing here is calibrated in advance.

Groww's exact response schema for get_option_chain() isn't fully
documented, so parsing below is defensive -- it tries several common
field-name variants and prints a clear diagnostic (once) if the shape
doesn't match anything expected, rather than silently returning
nonsense.
"""

from __future__ import annotations

from datetime import datetime, timedelta


class OptionsFlowProvider:

    def __init__(self, groww_client):
        self.groww = groww_client
        self._previous_oi = {}   # {(symbol, strike, option_type): oi}
        self._schema_warned = False

    def _get_nearest_expiry(self, exchange: str, underlying: str) -> str | None:
        try:
            today = datetime.now()
            response = self.groww.get_expiries(
                exchange=exchange,
                underlying_symbol=underlying,
                year=today.year,
                month=today.month,
            )
        except Exception as error:
            print(f"⚠️ Could not fetch expiries for {underlying}: {error}")
            return None

        expiries = self._extract_list(response, ["expiries", "expiry_dates", "data"])

        if not expiries:
            return None

        # Pick the nearest expiry that hasn't passed yet.
        today_str = today.strftime("%Y-%m-%d")
        future = sorted(e for e in expiries if isinstance(e, str) and e >= today_str)

        return future[0] if future else sorted(expiries)[0]

    @staticmethod
    def _extract_list(response, candidate_keys):
        if isinstance(response, list):
            return response
        if isinstance(response, dict):
            for key in candidate_keys:
                if key in response and isinstance(response[key], list):
                    return response[key]
        return []

    def _extract_strike_row(self, row):
        """
        Defensively pulls (strike, call_oi, put_oi, call_vol, put_vol)
        out of one option-chain row, trying multiple plausible field
        naming conventions since the exact schema isn't documented.
        """

        def pick(d, *keys, default=0):
            for k in keys:
                if isinstance(d, dict) and k in d and d[k] is not None:
                    return d[k]
            return default

        strike = pick(row, "strikePrice", "strike_price", "strike")

        call = row.get("CE") or row.get("call") or row.get("callOption") or {}
        put = row.get("PE") or row.get("put") or row.get("putOption") or {}

        call_oi = pick(call, "openInterest", "open_interest", "oi")
        put_oi = pick(put, "openInterest", "open_interest", "oi")
        call_vol = pick(call, "volume", "totalTradedVolume", "vol")
        put_vol = pick(put, "volume", "totalTradedVolume", "vol")

        return strike, call_oi, put_oi, call_vol, put_vol

    def analyze(self, symbol: str) -> dict | None:
        """
        Returns:
        {
            "pcr_oi": float, "pcr_volume": float,
            "max_pain_strike": float,
            "oi_shift_bias": "BULLISH" | "BEARISH" | "NEUTRAL",
            "direction": "UP" | "DOWN" | "SIDEWAYS",   # for adaptive engine
            "confidence": float,                        # for adaptive engine
            "strikes_analyzed": int,
        }
        or None if data couldn't be fetched/parsed (fails safe --
        never crashes the caller).
        """

        exchange_map = {"NIFTY": "NSE", "SENSEX": "BSE"}
        exchange = exchange_map.get(symbol)

        if not exchange:
            return None

        expiry = self._get_nearest_expiry(exchange, symbol)

        if not expiry:
            return None

        try:
            response = self.groww.get_option_chain(
                exchange=exchange,
                underlying=symbol,
                expiry_date=expiry,
            )
        except Exception as error:
            print(f"⚠️ Options chain fetch failed for {symbol}: {error}")
            return None

        rows = self._extract_list(response, ["optionChain", "option_chain", "data", "strikes"])

        if not rows:
            if not self._schema_warned:
                print(
                    f"⚠️ Options chain response for {symbol} didn't match "
                    f"any expected shape. Raw keys: "
                    f"{list(response.keys()) if isinstance(response, dict) else type(response)}. "
                    f"Options signal disabled until this is fixed."
                )
                self._schema_warned = True
            return None

        total_call_oi = 0
        total_put_oi = 0
        total_call_vol = 0
        total_put_vol = 0
        oi_shifts = []
        max_pain_candidates = []

        for row in rows:
            strike, call_oi, put_oi, call_vol, put_vol = self._extract_strike_row(row)

            if strike is None:
                continue

            total_call_oi += call_oi or 0
            total_put_oi += put_oi or 0
            total_call_vol += call_vol or 0
            total_put_vol += put_vol or 0

            call_key = (symbol, strike, "CE")
            put_key = (symbol, strike, "PE")

            prev_call_oi = self._previous_oi.get(call_key)
            prev_put_oi = self._previous_oi.get(put_key)

            if prev_call_oi is not None:
                oi_shifts.append(("CE", strike, (call_oi or 0) - prev_call_oi))
            if prev_put_oi is not None:
                oi_shifts.append(("PE", strike, (put_oi or 0) - prev_put_oi))

            self._previous_oi[call_key] = call_oi or 0
            self._previous_oi[put_key] = put_oi or 0

            max_pain_candidates.append((strike, (call_oi or 0) + (put_oi or 0)))

        if total_call_oi == 0 and total_put_oi == 0:
            return None

        pcr_oi = round(total_put_oi / total_call_oi, 3) if total_call_oi else None
        pcr_volume = round(total_put_vol / total_call_vol, 3) if total_call_vol else None

        max_pain_strike = (
            max(max_pain_candidates, key=lambda x: x[1])[0]
            if max_pain_candidates else None
        )

        # Net OI shift: positive = call OI building faster than put OI
        # (bullish positioning build-up), negative = the reverse.
        net_call_shift = sum(v for t, s, v in oi_shifts if t == "CE")
        net_put_shift = sum(v for t, s, v in oi_shifts if t == "PE")
        net_shift = net_call_shift - net_put_shift

        pcr_for_bias = pcr_oi if pcr_oi is not None else 1.0

        if net_shift > 0 and pcr_for_bias < 1.1:
            bias = "BULLISH"
            direction = "UP"
            confidence = min(70.0, 50.0 + abs(net_shift) / 1000)
        elif net_shift < 0 and pcr_for_bias > 0.9:
            bias = "BEARISH"
            direction = "DOWN"
            confidence = min(70.0, 50.0 + abs(net_shift) / 1000)
        else:
            bias = "NEUTRAL"
            direction = "SIDEWAYS"
            confidence = 40.0

        return {
            "pcr_oi": pcr_oi,
            "pcr_volume": pcr_volume,
            "max_pain_strike": max_pain_strike,
            "oi_shift_bias": bias,
            "direction": direction,
            "confidence": round(confidence, 1),
            "strikes_analyzed": len(max_pain_candidates),
            "expiry": expiry,
        }
