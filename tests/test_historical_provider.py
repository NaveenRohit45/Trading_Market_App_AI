

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.historical_provider import HistoricalProvider

provider = HistoricalProvider()

candles = provider.get_candles("NIFTY")

print("Total candles:", len(candles))

if candles:
    print(candles[0])
    print(candles[-1])