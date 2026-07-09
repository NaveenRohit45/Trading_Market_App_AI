import asyncio

from backend.data.groww_provider import GrowwProvider


async def main():

    provider = GrowwProvider()

    await provider.start()

    prices = await provider.get_prices()

    print()
    print("=" * 60)
    print("FINAL REAL MARKET PRICES")
    print("=" * 60)
    print("NIFTY :", prices["NIFTY"])
    print("SENSEX:", prices["SENSEX"])


asyncio.run(main())