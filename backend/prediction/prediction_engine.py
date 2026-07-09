import math

def _softmax(scores):
    ex = [math.exp(max(-20,min(20,s))) for s in scores]
    z = sum(ex)
    return [x/z for x in ex]

def predict(analysis, peer, news_score, horizon):
    # Experimental V1 heuristic. Replace with calibrated ML in V2.
    atr = max(analysis["atr"], 1e-6)
    trend = (analysis["ema_fast"] - analysis["ema_slow"]) / atr
    momentum = analysis["momentum"] / atr
    rsi_bias = (analysis["rsi"] - 50) / 25
    peer_dir = 1 if peer["state"]=="BULLISH" else -1 if peer["state"]=="BEARISH" else 0
    own_dir = 1 if analysis["state"]=="BULLISH" else -1 if analysis["state"]=="BEARISH" else 0
    confirm = 1 if own_dir != 0 and own_dir == peer_dir else -0.35 if own_dir*peer_dir < 0 else 0
    decay = {3:1.0, 5:0.82, 10:0.58}[horizon]
    directional = decay*(1.2*trend + 0.8*momentum + 0.35*rsi_bias + 0.55*peer_dir + 0.4*news_score)
    strength = abs(directional) + max(confirm,0)
    up, down, side = _softmax([directional, -directional, 0.65-strength])
    probs = {"UP": round(up*100,1), "DOWN": round(down*100,1), "SIDEWAYS": round(side*100,1)}
    direction = max(probs, key=probs.get)
    confidence = probs[direction]
    return {"horizon": horizon, "probabilities": probs, "direction": direction,
            "confidence": confidence, "experimental": True}

def combined_verdict(a, b):
    if a["state"] == b["state"] and a["state"] != "NO-TRADE":
        return {"verdict": a["state"], "confirmation": "CONFIRMING"}
    if a["state"] != "NO-TRADE" and b["state"] != "NO-TRADE":
        return {"verdict": "NO-TRADE", "confirmation": "DIVERGING"}
    return {"verdict": "NO-TRADE", "confirmation": "MIXED"}
