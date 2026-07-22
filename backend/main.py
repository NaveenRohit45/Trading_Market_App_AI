from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.config import BASE_DIR, settings
from backend.models import NewsInput
from backend.services.market_service import service
from backend.auth import AuthMiddleware, login_page, handle_login_submit

@asynccontextmanager
async def lifespan(app):
    await service.start()
    yield
    await service.stop()

app = FastAPI(title="ADA Market Intelligence", version="1.0.0", lifespan=lifespan)
app.add_middleware(AuthMiddleware)
app.mount("/static", StaticFiles(directory=BASE_DIR/"frontend"), name="static")

@app.get("/login")
def login_get(error: int = 0):
    return login_page(error=bool(error))

@app.post("/login")
def login_post(password: str = Form(...)):
    return handle_login_submit(password)

@app.get("/")
def home(): return FileResponse(BASE_DIR/"frontend"/"index.html")

@app.get("/api/status")
def status():
    return {
        "mode": settings.app_mode,
        "running": service.running,
        "error": service.error,
        "groww_configured": bool(
            settings.groww_api_key
            and settings.groww_api_secret
        ),
    }

@app.get("/api/snapshot")
def snapshot(): return service.latest

@app.get("/api/history")
def history(limit:int=100): return service.db.history(min(limit,1000))

@app.get("/api/accuracy")
def accuracy(): return service.db.accuracy()

@app.get("/api/replay")
def replay(symbol: str = "NIFTY", limit: int = 200): return service.db.replay_session(symbol, min(limit, 500))

@app.get("/api/failure-reasons")
def failure_reasons(symbol: str | None = None, min_occurrences: int = 3):
    return service.db.failure_reason_stats(symbol, min_occurrences)

@app.get("/api/candles")
def candles(symbol: str = "NIFTY", interval: int = 60, limit: int = 200):
    VALID_INTERVALS = {60, 120, 180, 300, 600, 1800, 3600, 86400}
    if interval not in VALID_INTERVALS:
        return {"error": f"interval must be one of {sorted(VALID_INTERVALS)}"}
    raw = service.engine.series(symbol, interval, include_current=True)
    trimmed = raw[-min(limit, 1000):]
    return [
        {"ts": c.start_ts, "open": c.open, "high": c.high, "low": c.low, "close": c.close, "volume": c.volume}
        for c in trimmed
    ]

@app.post("/api/settings/prediction-cycle")
def set_prediction_cycle(seconds: int):
    # Runtime-adjustable prediction cadence -- the live loop reads
    # settings.prediction_interval_seconds fresh every cycle, so this
    # takes effect on the very next cycle, no restart needed.
    if seconds < 30 or seconds > 3600:
        return {"ok": False, "error": "seconds must be between 30 and 3600"}
    settings.prediction_interval_seconds = seconds
    return {"ok": True, "prediction_interval_seconds": seconds}

@app.post("/api/news")
def add_news(item:NewsInput):
    service.news.add(item)
    return {"ok":True}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):

    print("🔵 WebSocket connection request")

    await ws.accept()

    print("🟢 WebSocket accepted")

    service.clients.add(ws)

    print(f"👥 Total Clients: {len(service.clients)}")

    try:

        while True:

            msg = await ws.receive_text()

            print("📨 Received:", msg)

    except Exception as e:

        print("🔴 WebSocket disconnected:", e)

        service.clients.discard(ws)
