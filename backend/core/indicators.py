import numpy as np

def ema(values, period):
    if not values: return 0.0
    a = 2 / (period + 1)
    out = float(values[0])
    for v in values[1:]:
        out = a * float(v) + (1-a) * out
    return out

def rsi(values, period=14):
    if len(values) < 3: return 50.0
    x = np.asarray(values[-(period+1):], dtype=float)
    d = np.diff(x)
    gains = np.clip(d, 0, None)
    losses = np.clip(-d, 0, None)
    ag = gains.mean() if len(gains) else 0
    al = losses.mean() if len(losses) else 0
    if al == 0: return 100.0 if ag > 0 else 50.0
    rs = ag / al
    return float(100 - 100/(1+rs))

def atr(candles, period=14):
    if len(candles) < 2: return 0.0
    trs = []
    for i in range(1, len(candles)):
        c, p = candles[i], candles[i-1]
        trs.append(max(c.high-c.low, abs(c.high-p.close), abs(c.low-p.close)))
    return float(np.mean(trs[-period:]))

def slope(values, lookback=6):
    y = np.asarray(values[-lookback:], dtype=float)
    if len(y) < 2: return 0.0
    x = np.arange(len(y))
    return float(np.polyfit(x, y, 1)[0])
