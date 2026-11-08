from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

# Import Routers
from routers.logs import router as logs_router 
from routers.alerts import router as alerts_router
from routers.config import router as config_router
from routers.blocked_ips import router as blocked_ips_router
from routers.stats import router as stats_router

# Import Database & WebSocket Manager
from app.database import Database, SessionLocal
from app.models import TrafficLog
from app.ws_manager import manager

async def stream_traffic_data():
    while True:
        await asyncio.sleep(1) # Lặp lại sau mỗi 1 giây
        db = SessionLocal()
        try:
            # Lấy 5 log mạng mới nhất để vẽ biểu đồ
            recent_logs = db.query(TrafficLog).order_by(TrafficLog.id.desc()).limit(5).all()
            if recent_logs:
                data = [{"ip": log.source_ip, "size": log.packet_size} for log in recent_logs]
                await manager.broadcast({"type": "traffic_stream", "data": data})
        except Exception as e:
            print(f"Lỗi Stream: {e}")
        finally:
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phần này chạy khi server khởi động
    task = asyncio.create_task(stream_traffic_data())
    yield
    # Phần này chạy khi server tắt
    task.cancel()

app = FastAPI(
    title="PBL4 Mail NIDS API",
    description="RESTful API Base với cấu trúc Router, Connection Pool và WebSocket",
    version="1.1.0",
    lifespan=lifespan
)

# 3. Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Đăng ký các Router 
app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(blocked_ips_router)
app.include_router(config_router)
app.include_router(stats_router)

@app.get("/", tags=["Health Check"])
def health_check():
    """Hàm kiểm tra trạng thái hoạt động của Server và Database"""
    db = Database()
    db_status = db.check_db_status()
    
    return {
        "api_status": "OK",
        "database_connected": db_status,
        "message": "NIDS Backend Server sẵn sàng!"
    }

# --- MỞ ENDPOINT WEBSOCKET ---
@app.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Giữ kết nối luôn mở
    except WebSocketDisconnect:
        manager.disconnect(websocket)