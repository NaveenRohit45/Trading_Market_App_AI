import asyncio
import json
import time
from pathlib import Path

from growwapi import GrowwAPI, GrowwFeed

from backend.config import settings
from backend.models import Candle


class GrowwProvider:

    @staticmethod
    def _get_access_token_with_full_diagnostics(api_key, secret):
        """
        Groww's SDK swallows its own error response and just raises a
        generic "Bad Request" on 400, which makes real auth problems
        (expired key, malformed .env value, wrong auth mode) very
        hard to diagnose. This calls the same endpoint directly so we
        can print Groww's ACTUAL error text before falling back to
        the SDK's own (less informative) exception.
        """

        import requests

        # Common .env authoring mistake: wrapping the value in quotes,
        # e.g. GROWW_API_KEY="abc123" -- python-dotenv does NOT strip
        # these, so the literal quote characters end up IN the key,
        # silently breaking auth. Strip stray quotes/whitespace defensively.
        clean_key = (api_key or "").strip().strip('"').strip("'")
        clean_secret = (secret or "").strip().strip('"').strip("'")

        if clean_key != api_key or clean_secret != secret:
            print(
                "⚠️  GROWW_API_KEY or GROWW_API_SECRET in .env had stray "
                "quotes/whitespace -- stripped automatically, but fix "
                "your .env file to avoid relying on this."
            )

        # Groww issues two DIFFERENT key types from their API
        # dashboard: "approval" mode (send the secret directly) and
        # "TOTP" mode (the secret is actually a TOTP seed -- you must
        # generate a live rotating 6-digit code from it with each
        # request, same as an authenticator app). Groww's error
        # response tells us which one a given key expects
        # ("totp value cannot be empty" = this key is TOTP-mode), so
        # we try TOTP mode first since that's what regenerated keys
        # commonly default to, and fall back to secret-mode.

        def _try_auth(payload):
            return requests.post(
                "https://api.groww.in/v1/token/api/access",
                headers={
                    "Authorization": f"Bearer {clean_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=15,
            )

        try:
            import pyotp
        except ImportError:
            print(
                "⚠️  pyotp not installed -- run: pip install pyotp "
                "--break-system-packages (or pip install -r requirements.txt). "
                "Falling back to secret-mode auth for now, which will "
                "fail if your key is TOTP-mode."
            )
            try:
                response = _try_auth({"secret": clean_secret})
            except Exception as network_error:
                print(f"❌ Could not reach Groww's auth endpoint at all: {network_error}")
                raise
        else:
            try:
                # TOTP seeds are commonly DISPLAYED with spaces for
                # readability (e.g. "ABCD EFGH IJKL") when Groww shows
                # them to you -- but base32 decoding requires no
                # whitespace. Also normalize case, since base32 is
                # case-insensitive but some clipboards/fonts confuse
                # lowercase L/1, O/0 when hand-typed.
                totp_seed = clean_secret

                # Auto-recover the common case: pasting the full
                # "otpauth://..." URI (what a QR code actually
                # encodes) instead of just the secret text. Extract
                # the real secret parameter automatically.
                if "otpauth://" in totp_seed or "secret=" in totp_seed:
                    import re
                    match = re.search(r"[?&]secret=([A-Za-z2-7]+)", totp_seed)
                    if match:
                        print(
                            "⚠️  GROWW_API_SECRET looked like a full otpauth:// "
                            "URI, not a bare secret -- extracted the secret "
                            "parameter from it automatically."
                        )
                        totp_seed = match.group(1)

                totp_seed = totp_seed.replace(" ", "").replace("-", "").upper()

                # Print exactly what's wrong with the string, without
                # needing to see the actual secret value -- length and
                # which specific characters are invalid is enough to
                # diagnose this without exposing the credential.
                valid_base32_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=")
                invalid_chars = sorted(set(
                    ch for ch in totp_seed if ch not in valid_base32_chars
                ))

                print("=" * 60)
                print("TOTP SECRET DIAGNOSTIC (no credential values shown)")
                print(f"Length: {len(totp_seed)} characters")
                print(f"Invalid characters found: {invalid_chars if invalid_chars else 'none'}")
                if invalid_chars:
                    print(
                        "Base32 only allows A-Z and 2-7. If you see 0, 1, "
                        "8, or 9 above, or lowercase letters, or symbols "
                        "like ':', '/', '_', '-' -- the value in "
                        "GROWW_API_SECRET is NOT a plain base32 TOTP seed. "
                        "This often happens if you copied a full "
                        "'otpauth://...' URL or a QR-code payload instead "
                        "of just the secret text Groww showed underneath it."
                    )
                print("=" * 60)

                try:
                    totp_code = pyotp.TOTP(totp_seed).now()
                except Exception as decode_error:
                    print("=" * 60)
                    print(f"❌ GROWW_API_SECRET is not a valid TOTP seed: {decode_error}")
                    print(
                        "This should be the base32 TOTP secret Groww showed you "
                        "when you generated this API key (NOT your Groww "
                        "account password, NOT the API key itself, and NOT a "
                        "6-digit code -- those all expire/rotate). If you're "
                        "not sure you copied the right value, regenerate the "
                        "key on Groww's API dashboard and copy the TOTP "
                        "secret shown at that moment -- it's usually only "
                        "shown once."
                    )
                    print("=" * 60)
                    raise

                response = _try_auth({"totp": totp_code})

                if response.status_code == 400:
                    print(
                        "TOTP-mode auth failed, retrying with secret-mode "
                        "in case this key is the older 'approval' type..."
                    )
                    response = _try_auth({"secret": clean_secret})

            except Exception as network_error:
                print(f"❌ Could not reach Groww's auth endpoint at all: {network_error}")
                raise

        if not response.ok:
            print("=" * 60)
            print(f"❌ GROWW AUTH FAILED -- HTTP {response.status_code}")
            print(f"Raw response body: {response.text}")
            print("=" * 60)
            print(
                "Common causes: (1) the API key/secret pair has "
                "expired -- Groww's 'approval' mode keys are often "
                "only valid ~24 hours and need regenerating daily on "
                "the Groww API dashboard, (2) the key/secret were "
                "copy-pasted with extra characters, (3) this key was "
                "generated for TOTP mode, not secret/approval mode, "
                "or vice versa."
            )
            response.raise_for_status()

        return response.json()["token"]


    def __init__(self):

        print("=" * 60)
        print("CONNECTING TO GROWW")
        print("=" * 60)

        if settings.groww_access_token:
            # Simplest, most reliable path: a long-lived token
            # generated directly from Groww's dashboard. No TOTP, no
            # secret exchange, no expiry surprises from this code's
            # side. Use this if you have it.
            print("Using GROWW_ACCESS_TOKEN directly (skipping TOTP/secret exchange).")
            access_token = settings.groww_access_token.strip().strip('"').strip("'")

        else:
            if not settings.groww_api_key:
                raise RuntimeError(
                    "GROWW_API_KEY is missing from .env"
                )

            if not settings.groww_api_secret:
                raise RuntimeError(
                    "GROWW_API_SECRET is missing from .env"
                )

            access_token = self._get_access_token_with_full_diagnostics(
                settings.groww_api_key,
                settings.groww_api_secret,
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