"""
Trading Market AI

Groww Option Chain API Discovery

This file is used ONLY to inspect
the Groww SDK before implementing
option_chain_fetcher.py.
"""

import sys
import json
import inspect
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from growwapi import GrowwAPI
from backend.config import settings


# ==========================================================
# LOGIN
# ==========================================================

print("=" * 70)
print("CONNECTING TO GROWW")
print("=" * 70)

token = GrowwAPI.get_access_token(
    api_key=settings.groww_api_key,
    secret=settings.groww_api_secret,
)

client = GrowwAPI(token)

print("✅ Connected")


# ==========================================================
# METHOD SIGNATURES
# ==========================================================

print()
print("=" * 70)
print("METHOD SIGNATURES")
print("=" * 70)

methods = [

    "get_expiries",

    "get_option_chain",

    "get_contracts",

    "get_greeks",

]

for method_name in methods:

    print()

    print("-" * 70)

    print(method_name)

    print("-" * 70)

    method = getattr(
        client,
        method_name,
    )

    print("Signature:")

    print(inspect.signature(method))

    print()

    print("Docstring:")

    print(method.__doc__)


# ==========================================================
# GET NIFTY INSTRUMENT
# ==========================================================

print()
print("=" * 70)
print("NIFTY INSTRUMENT")
print("=" * 70)

instrument = client.get_instrument_by_exchange_and_trading_symbol(

    exchange="NSE",

    trading_symbol="NIFTY",

)

print(json.dumps(
    instrument,
    indent=4,
    default=str,
))


# ==========================================================
# AVAILABLE ATTRIBUTES
# ==========================================================

print()
print("=" * 70)
print("INSTRUMENT KEYS")
print("=" * 70)

for key in instrument.keys():

    print(key)


# ==========================================================
# UNDERLYING SYMBOL
# ==========================================================

print()
print("=" * 70)
print("IMPORTANT VALUES")
print("=" * 70)

for key in [

    "exchange",

    "segment",

    "exchange_token",

    "groww_symbol",

    "trading_symbol",

    "underlying_symbol",

]:

    print(f"{key:20} : {instrument.get(key)}")


# ==========================================================
# TRY GET EXPIRIES
# ==========================================================

print()
print("=" * 70)
print("TRYING get_expiries()")
print("=" * 70)

try:

    expiries = client.get_expiries(

        exchange="NSE",

        underlying_symbol="NIFTY",

    )

    print(json.dumps(
        expiries,
        indent=4,
        default=str,
    ))

except Exception as e:

    print()

    print("❌ get_expiries FAILED")

    print(type(e).__name__)

    print(e)


# ==========================================================
# TRY CONTRACTS
# ==========================================================

print()
print("=" * 70)
print("TRYING get_contracts()")
print("=" * 70)

try:

    contracts = client.get_contracts(

        exchange="NSE",

        underlying_symbol="NIFTY",

    )

    print(json.dumps(
        contracts,
        indent=4,
        default=str,
    )[:4000])

except Exception as e:

    print()

    print("❌ get_contracts FAILED")

    print(type(e).__name__)

    print(e)


print()
print("=" * 70)
print("DISCOVERY COMPLETE")
print("=" * 70)