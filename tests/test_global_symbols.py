"""
============================================================
Trading Market AI
Global Symbol Discovery Test
============================================================

Purpose

Verify all global market symbols before building
GlobalProvider.

Author : Super Cat
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests

from backend.config import settings


BASE_URL = "https://finnhub.io/api/v1"

TOKEN = settings.finnhub_api_key


# ==========================================================
# QUOTE
# ==========================================================

def quote(symbol):

    url = f"{BASE_URL}/quote"

    response = requests.get(

        url,

        params={

            "symbol": symbol,

            "token": TOKEN,

        },

        timeout=15,

    )

    return response.json()


# ==========================================================
# SYMBOLS TO VERIFY
# ==========================================================

SYMBOLS = {

    # ------------------------
    # US Markets
    # ------------------------

    "Dow Jones"      : "^DJI",
    "NASDAQ"         : "^IXIC",
    "S&P500"         : "^GSPC",

    # ------------------------
    # Asia
    # ------------------------

    "Nikkei"         : "^N225",
    "Hang Seng"      : "^HSI",
    "Shanghai"       : "000001.SS",

    # ------------------------
    # India
    # ------------------------

    "Gift Nifty"     : "^NSEI",
    "India VIX"      : "^INDIAVIX",

    # ------------------------
    # Currency
    # ------------------------

    "USDINR"         : "OANDA:USD_INR",

    # ------------------------
    # Commodities
    # ------------------------

    "Gold"           : "OANDA:XAU_USD",
    "Crude Oil"      : "OANDA:BCO_USD",

}


# ==========================================================
# MAIN
# ==========================================================

def run():

    print("=" * 70)
    print("GLOBAL SYMBOL DISCOVERY")
    print("=" * 70)

    for name, symbol in SYMBOLS.items():

        print()

        print("-" * 70)
        print(name)
        print("Symbol :", symbol)

        try:

            data = quote(symbol)

            print(data)

        except Exception as e:

            print("FAILED")

            print(e)


if __name__ == "__main__":

    run()