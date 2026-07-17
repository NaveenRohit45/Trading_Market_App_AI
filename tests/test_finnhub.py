"""
============================================================
Finnhub Connection Test
============================================================
"""


from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import requests

from backend.config import settings


API_KEY = settings.finnhub_api_key

BASE_URL = "https://finnhub.io/api/v1"


def quote(symbol):

    url = f"{BASE_URL}/quote"

    response = requests.get(

        url,

        params={

            "symbol": symbol,

            "token": API_KEY,

        },

        timeout=10,

    )

    response.raise_for_status()

    return response.json()


def main():

    print("=" * 60)

    print("FINNHUB CONNECTION TEST")

    print("=" * 60)

    print()

    print("Testing Apple (AAPL)...")

    data = quote("AAPL")

    print(data)


if __name__ == "__main__":

    main()