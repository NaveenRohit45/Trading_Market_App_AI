from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.candle_engine import CandleEngine
from backend.services.historical_loader import HistoricalLoader

engine = CandleEngine()
loader = HistoricalLoader(engine)

stats = loader.load_all_timeframes("NIFTY")

print(stats)

print("1m :", len(engine.series("NIFTY", 60)))
print("2m :", len(engine.series("NIFTY", 120)))
print("3m :", len(engine.series("NIFTY", 180)))
print("5m :", len(engine.series("NIFTY", 300)))