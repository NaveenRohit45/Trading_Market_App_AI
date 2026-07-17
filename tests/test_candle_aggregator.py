from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.historical_provider import HistoricalProvider
from backend.core.candle_aggregator import CandleAggregator

provider = HistoricalProvider()

candles_1m = provider.get_candles("NIFTY")

candles_3m = CandleAggregator.aggregate(
    candles_1m,
    timeframe_minutes=3,
)

print(f"1m Candles : {len(candles_1m)}")
print(f"3m Candles : {len(candles_3m)}")

print()
print("FIRST")
print(candles_3m[0])

print()
print("LAST")
print(candles_3m[-1])