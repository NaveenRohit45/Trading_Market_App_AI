import time

from growwapi import GrowwAPI, GrowwFeed

from backend.config import settings


print("=" * 60)
print("NIFTY INDEX STREAM TEST")
print("=" * 60)


access_token = GrowwAPI.get_access_token(
    api_key=settings.groww_api_key,
    secret=settings.groww_api_secret,
)

groww = GrowwAPI(access_token)

print("✅ Groww authenticated")


feed = GrowwFeed(groww)

print("✅ GrowwFeed created")


sensex = [
    {
        "exchange": "BSE",
        "segment": "CASH",
        "exchange_token": "1",
    }
]


print("Subscribing to NIFTY index stream...")


result = feed.subscribe_index_value(
    sensex
)

print("SUBSCRIBE RESULT:")
print(result)


for i in range(20):

    time.sleep(1)

    try:

        value = feed.get_index_value()

        print(
            f"[{i + 1:02d}]",
            value
        )

    except Exception as error:

        print(
            f"[{i + 1:02d}] "
            f"{type(error).__name__}: {error}"
        )