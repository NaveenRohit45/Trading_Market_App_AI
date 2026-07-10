# Trading_Market_App_AI

A complete local **analysis + shadow-prediction** application for NIFTY 50 and SENSEX.

## What works now
- Dark dashboard matching the concept design
- DEMO mode runs immediately with a realistic market simulator
- GROWW mode uses the official `growwapi` SDK and bulk LTP polling
- NIFTY + SENSEX confirmation/divergence
- 3m / 5m / 10m experimental probability forecasts
- Trend, RSI, EMA, VWAP proxy, volatility, breakout and regime analysis
- News-intelligence input API (manual/source-adapter ready)
- Prediction history stored in SQLite
- Automatic outcome scoring
- Accuracy page
- Alerts only on meaningful state changes
- WebSocket dashboard updates

## Important
V1 probabilities are **experimental heuristic probabilities**, not a trained edge and not guaranteed trade signals.
Run in shadow mode first. Do not connect automatic order placement.

## Start
1. Extract the ZIP.
2. Double-click `run.bat`.
3. The browser opens at `http://127.0.0.1:8000`.

## Groww live mode
1. Copy `.env.example` to `.env`.
2. Set:
   `APP_MODE=GROWW`
3. Add your token locally:
   `GROWW_API_TOKEN=...`
4. Restart.

Never paste your token into chat or commit `.env`.

The default Groww symbols are `NSE_NIFTY` and `BSE_SENSEX`. If your account/SDK returns a different symbol mapping, edit `backend/config.py`.

## Architecture
- `backend/data`: demo and Groww providers
- `backend/core`: indicators, candle building, feature extraction
- `backend/analyzers`: market structure and news state
- `backend/prediction`: probability and outcome scoring
- `backend/services`: live engine and persistence
- `frontend`: dashboard

## API
- `GET /api/status`
- `GET /api/snapshot`
- `GET /api/history?limit=100`
- `GET /api/accuracy`
- `POST /api/news`
- `WS /ws`

## Next upgrade path
V2 should replace heuristic probability generation with walk-forward trained models using stored snapshots and historical candles. Keep train/test separation by date and calibrate probabilities before trusting confidence scores.
