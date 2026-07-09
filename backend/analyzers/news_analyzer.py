from collections import deque
import time

class NewsAnalyzer:
    def __init__(self):
        self.items = deque(maxlen=50)

    def add(self, item):
        self.items.appendleft({"headline": item.headline, "sentiment": item.sentiment,
                               "impact": item.impact, "source": item.source, "ts": time.time()})

    def score(self):
        now = time.time()
        total = weight = 0.0
        for x in self.items:
            age_hours = (now-x["ts"])/3600
            decay = 0.5 ** (age_hours/2)
            sign = 1 if x["sentiment"]=="positive" else -1 if x["sentiment"]=="negative" else 0
            w = x["impact"] * decay
            total += sign*w; weight += w
        return round(total/max(weight,1e-9),3) if weight else 0.0

    def latest(self, n=5):
        return list(self.items)[:n]
