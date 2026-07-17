from collections import defaultdict, deque
from backend.models import Candle

class CandleEngine:
    def __init__(self, maxlen=5000):
        self.candles = defaultdict(lambda: deque(maxlen=maxlen))
        self.current = {}

    def add_tick(self, symbol, price, ts, interval=60):
        bucket = int(ts // interval) * interval
        key = (symbol, interval)
        c = self.current.get(key)
        closed = None
        if c is None or c.start_ts != bucket:
            if c is not None:
                self.candles[key].append(c)
                closed = c
            c = Candle(symbol=symbol, start_ts=bucket, open=price, high=price, low=price, close=price)
            self.current[key] = c
        else:
            c.high = max(c.high, price)
            c.low = min(c.low, price)
            c.close = price
        return closed

    def series(self, symbol, interval=60, include_current=True):
        out = list(self.candles[(symbol, interval)])
        c = self.current.get((symbol, interval))
        if include_current and c: out.append(c)
        return out

    # ==========================================================
    # Load Historical Candles
    # ==========================================================

    def load_history(
            self,
            symbol,
            interval,
            candles,
    ):
        """
        Load completed historical candles into the engine.
        """

        key = (symbol, interval)

        self.candles[key].clear()

        for candle in candles:
            self.candles[key].append(candle)

        # No current candle yet.
        self.current.pop(key, None)
