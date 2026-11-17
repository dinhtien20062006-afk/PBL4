"""FastAPI entry point.  Chạy:  uvicorn app.main:app --reload --port 8000  (từ thư mục backend/)"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import CORS_ORIGINS
from app.database import Database
from app.routers import alerts, attack, blocked_ips, config, logs, stats
from app.ws_manager import manager

logger = logging.getLogger("nids")
TICK_SECONDS = 2


async def traffic_ticker():
    """Đẩy tốc độ gói tin/giây cho Dashboard (frontend lắng nghe `traffic_tick`).

    Chỉ truy vấn khi có client đang kết nối; truy vấn đi qua cache TTL nên không quét bảng mỗi tick.
    """
    while True:
        await asyncio.sleep(TICK_SECONDS)
        if not manager.active_connections:
            continue
        try:
            _total, last_minute, _alerts = await asyncio.to_thread(stats._packet_totals)
            await manager.broadcast(
                {"type": "traffic_tick", "data": {"packets_per_second": round(last_minute / 60, 2)}}
            )
        except Exception as exc:  # DB tạm thời lỗi: bỏ qua tick này
            logger.warning("traffic_tick lỗi: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(traffic_ticker())
    yield
    task.cancel()


app = FastAPI(
    title="PBL4 Mail NIDS API",
    description="REST API + WebSocket cho Dashboard giám sát NIDS",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(blocked_ips.router)
app.include_router(blocked_ips.compat_router)
app.include_router(config.router)
app.include_router(stats.router)
app.include_router(attack.router)


@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "api_status": "OK",
        "database_connected": Database().check_db_status(),
        "message": "NIDS Backend Server sẵn sàng!",
    }


@app.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # giữ kết nối; client không cần gửi gì
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("WebSocket lỗi: %s", exc)
    finally:
        manager.disconnect(websocket)
