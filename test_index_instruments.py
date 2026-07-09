from growwapi import GrowwAPI

from backend.config import settings


access_token = GrowwAPI.get_access_token(
    api_key=settings.groww_api_key,
    secret=settings.groww_api_secret
)

groww = GrowwAPI(access_token)

print("✅ Connected to Groww")
print("=" * 60)

tests = [
    ("NSE", "NIFTY"),
    ("NSE", "NIFTY 50"),
    ("BSE", "SENSEX"),
]

for exchange, symbol in tests:

    print()
    print(f"Testing: {exchange} / {symbol}")

    try:

        result = groww.get_instrument_by_exchange_and_trading_symbol(
            exchange=exchange,
            trading_symbol=symbol
        )

        print("RESULT:", result)

    except Exception as error:

        print(
            f"ERROR: {type(error).__name__}: {error}"
        )