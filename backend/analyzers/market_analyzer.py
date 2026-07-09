from backend.core.indicators import ema, rsi, atr, slope

def analyze(symbol, candles):
    closes = [c.close for c in candles]
    if len(closes) < 5:
        p = closes[-1] if closes else 0
        return {"symbol": symbol, "price": p, "state": "NO-TRADE", "regime": "WARMING UP",
                "rsi": 50, "ema_fast": p, "ema_slow": p, "atr": 0, "support": p, "resistance": p,
                "momentum": 0, "breakout": "NONE"}
    p = closes[-1]
    ef, es = ema(closes, 5), ema(closes, 13)
    rv, av = rsi(closes, 14), atr(candles, 14)
    mom = slope(closes, 6)
    recent = candles[-12:-1] if len(candles) > 2 else candles
    resistance = max(c.high for c in recent)
    support = min(c.low for c in recent)
    breakout = "UP" if p > resistance else "DOWN" if p < support else "NONE"
    bullish = p > ef > es and mom > 0
    bearish = p < ef < es and mom < 0
    if bullish: state = "BULLISH"
    elif bearish: state = "BEARISH"
    else: state = "NO-TRADE"
    spread = abs(ef-es) / max(av, 1e-9)
    regime = "TRENDING" if spread > 0.35 else "CHOPPY"
    return {"symbol": symbol, "price": round(p,2), "state": state, "regime": regime,
            "rsi": round(rv,2), "ema_fast": round(ef,2), "ema_slow": round(es,2),
            "atr": round(av,2), "support": round(support,2), "resistance": round(resistance,2),
            "momentum": round(mom,4), "breakout": breakout}
