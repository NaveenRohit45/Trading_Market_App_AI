from pydantic import BaseModel, Field
from typing import Literal
from dataclasses import dataclass
from typing import Optional

class Tick(BaseModel):
    symbol: str
    price: float
    ts: float

class Candle(BaseModel):
    symbol: str
    start_ts: float
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

class NewsInput(BaseModel):
    headline: str
    sentiment: Literal["positive", "negative", "neutral"] = "neutral"
    impact: float = Field(default=0.5, ge=0, le=1)
    source: str = "manual"


@dataclass(slots=True)
class InstrumentSnapshot:

    symbol: str

    ltp: float

    open: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    previous_close: Optional[float] = None

    change: Optional[float] = None

    change_percent: Optional[float] = None

    volume: Optional[float] = None


@dataclass(slots=True)
class MarketSnapshot:

    timestamp: float

    live: bool

    status: str

    nifty: InstrumentSnapshot

    sensex: InstrumentSnapshot
