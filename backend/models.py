from pydantic import BaseModel, Field
from typing import Literal

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
