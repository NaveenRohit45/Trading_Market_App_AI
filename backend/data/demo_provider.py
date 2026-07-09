import math, random, time

class DemoProvider:
    def __init__(self):
        self.t = 0
        self.base = {"NIFTY": 24250.0, "SENSEX": 77200.0}
        self.price = dict(self.base)
        self.regime = -0.10

    async def start(self): pass
    async def stop(self): pass

    async def get_prices(self):
        self.t += 1
        if self.t % 180 == 0:
            self.regime = random.choice([-0.18,-0.08,0,0.08,0.18])
        common = self.regime + random.gauss(0,0.42)
        self.price["NIFTY"] += common + 0.25*math.sin(self.t/11)
        self.price["SENSEX"] += common*3.15 + random.gauss(0,0.7)
        return dict(self.price)
