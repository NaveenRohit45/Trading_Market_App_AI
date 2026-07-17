from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.config import BASE_DIR, settings
from backend.models import NewsInput
from backend.services.market_service import service

@asynccontextmanager
async def lifespan(app):
    await service.start()
    yield
    await service.stop()

app = FastAPI(title="ADA Market Intelligence", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR/"frontend"), name="static")

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
