"""
AI Summary — Real AI Reasoning Layer

This is NOT the ML classifier (see prediction/train_model.py,
prediction/ml_predictor.py). That produces a numeric probability from
patterns in past price data. This module is genuinely different: it
uses an LLM (Claude) to *reason* across everything your app knows at
once -- price action, live market brain, global market brain, news
sentiment, the ML model's own prediction (if trained), and your
actual historical accuracy -- and produce a written analysis a human
scalper can sanity-check, including WHY it thinks what it thinks and
what could make it wrong.

Honest limitations, on purpose:
- This does not have a persistent edge over the market. Nothing does,
  reliably, at 3-10 minute horizons, from public price/indicator data.
- Treat every summary as one more input to your own judgment, not an
  instruction to execute a trade. This is decision support, not
  financial advice, and it will be wrong sometimes -- including
  confidently wrong.
- It costs a real API call each time it runs, so it's called on a
  slower cadence than the live price loop (see PREDICTION_INTERVAL_SECONDS
  in market_service.py), not on every 3-second tick.
"""

from __future__ import annotations

import json
import os

import httpx

from backend.config import settings

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """You are a market analysis assistant embedded in a live NSE/BSE index scalping dashboard.

You receive structured JSON describing:
- Current price, RSI, EMA, ATR, support/resistance for NIFTY and SENSEX
- Multiple rule-based "brain" outputs (price action, live market conditions, global markets)
- Options flow: Put-Call Ratio, max pain strike, open-interest shift bias (if available)
- Pattern memory: whether this exact market setup has been seen before, how many times, and the REAL historical win rate for it (if available)
- Candlestick patterns detected on the 5-minute chart (e.g. Bullish Engulfing, Doji, Morning Star) using textbook geometric definitions -- if present, weave these into your reasoning by name
- The app's own V1 heuristic forecast probabilities (UP/DOWN/SIDEWAYS) per horizon
- An ML model's prediction, IF one has been trained yet (may be absent -- say so plainly if missing)
- The app's actual historical accuracy for these symbols/horizons from real resolved predictions

Your job: write a concise, honest scalper-facing summary (120-200 words), in the style of a sharp human trading desk note -- specific price levels and concrete reasoning, not vague sentiment. For example, the target style is:

"Although momentum is bullish, heavy call writing exists at 24300 (options flow). There is a 73% probability price reaches 24260 before 24300 is tested, based on 17 similar historical setups (pattern memory) with a 65% win rate. Avoid buying above 24255 because risk/reward deteriorates near resistance."

Rules:
- State the single most likely near-term direction AND your actual confidence in it, grounded in specific price levels (support/resistance/max-pain strike), not generic language.
- If pattern memory shows real historical matches, CITE THE ACTUAL COUNT AND WIN RATE given to you (e.g. "seen this setup 17 times, 65% win rate") -- never invent a number if pattern memory data isn't provided or shows zero matches; say so plainly instead.
- If options flow data is present, weave in the PCR/max-pain/OI-shift bias as concrete reasoning (e.g. "heavy OI buildup near X suggests..."), not just a mentioned number.
- Explicitly call out when signals conflict between brains -- don't paper over disagreement.
- Reference the ACTUAL historical accuracy numbers given to you. If accuracy is low or the sample size is small, say that outright and downgrade your confidence language accordingly. Never claim confidence the data doesn't support.
- If no ML prediction is present, say the analysis is heuristic-only, not model-backed.
- End with one concrete risk/invalidation condition tied to a specific price level (what would prove this wrong).
- Never use hedge-free absolute language ("will happen", "guaranteed"). This is probabilistic decision support for a human, not an instruction to trade.
- No markdown headers, no bullet spam -- write it as prose a trader can read in 15-20 seconds.
"""


def _build_user_payload(symbol: str, snapshot: dict, accuracy_stats: list[dict]) -> dict:
    analysis = snapshot.get("analysis", {}).get(symbol, {})
    brains = snapshot.get("brains", {})
    forecast_v1 = snapshot.get("forecast", {}).get(symbol, [])
    forecast_ml = snapshot.get("forecast", {}).get(f"{symbol}_ML")

    relevant_accuracy = [
        row for row in accuracy_stats if row.get("symbol") == symbol
    ]

    options_data = snapshot.get("options", {}).get(symbol)
    pattern_data = snapshot.get("pattern_memory", {}).get(symbol)
    candlestick_data = snapshot.get("candlestick_patterns", {}).get(symbol)

    return {
        "symbol": symbol,
        "current_price": snapshot.get("prices", {}).get(symbol),
        "technical_snapshot": analysis,
        "brains": {
            "price_action": brains.get("price_action", {}).get(symbol),
            "live_market": brains.get("live_market", {}).get(symbol),
            "global_market": brains.get("global_market", {}),
            "decision": brains.get("decision", {}).get(symbol),
        },
        "options_flow": options_data if options_data else "NOT_AVAILABLE",
        "pattern_memory": (
            {
                "historical_matches": pattern_data.get("historical_matches"),
                "win_rate": pattern_data.get("win_rate"),
                "wins": pattern_data.get("wins"),
                "losses": pattern_data.get("losses"),
                "recommendation": pattern_data.get("recommendation"),
            }
            if pattern_data and pattern_data.get("historical_matches", 0) > 0
            else "NO_HISTORICAL_MATCHES_YET"
        ),
        "candlestick_patterns_detected": (
            candlestick_data.get("patterns")
            if candlestick_data and candlestick_data.get("patterns")
            else "NO_PATTERNS_DETECTED_THIS_CYCLE"
        ),
        "v1_heuristic_forecast": forecast_v1,
        "ml_model_forecast": forecast_ml if forecast_ml else "NO_TRAINED_MODEL_YET",
        "actual_historical_accuracy": (
            relevant_accuracy if relevant_accuracy
            else "NO_RESOLVED_HISTORY_YET"
        ),
    }


async def generate_ai_summary(symbol: str, snapshot: dict, accuracy_stats: list[dict], client: httpx.AsyncClient) -> dict:
    """
    Calls Claude to produce a reasoned market summary for one symbol.
    Returns {"symbol", "summary", "generated_at"} or an error dict --
    never raises, so a failed API call can't take down the live loop.
    """

    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key:
        return {
            "symbol": symbol,
            "summary": None,
            "error": "ANTHROPIC_API_KEY not set in .env -- AI summary disabled.",
        }

    payload = _build_user_payload(symbol, snapshot, accuracy_stats)

    try:
        response = await client.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
                "max_tokens": 400,
                "system": SYSTEM_PROMPT,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Current live snapshot for {symbol}:\n\n"
                            f"{json.dumps(payload, indent=2, default=str)}"
                        ),
                    }
                ],
            },
            timeout=20.0,
        )

        response.raise_for_status()

        data = response.json()

        text_blocks = [
            block["text"]
            for block in data.get("content", [])
            if block.get("type") == "text"
        ]

        summary_text = "\n".join(text_blocks).strip()

        return {
            "symbol": symbol,
            "summary": summary_text,
            "error": None,
        }

    except Exception as error:
        print(f"⚠️ AI summary generation failed for {symbol}: {error}")
        return {
            "symbol": symbol,
            "summary": None,
            "error": str(error),
        }
