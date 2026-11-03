from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
from datetime import datetime

from app.database import Database
from routers.logs import router as logs_router
from routers.alerts import router as alerts_router
from routers.blocked_ips import router as blocked_ips_router
from routers.ips import router as ips_router
from routers.stats import router as stats_router

app = FastAPI(
    title="PBL4 Mail NIDS API",
    description="RESTful API cho NIDS - dữ liệu thật từ MySQL",
    version="2.0.0",
)

# CORS: cho phép Frontend (Vite 5173 hoặc 3000) gọi sang Backend cổng 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(blocked_ips_router)
app.include_router(ips_router)
app.include_router(stats_router)


@app.get("/", tags=["Health Check"])
def health_check():
    db_status = Database().check_db_status()
    return {
        "api_status": "OK",
        "database_connected": db_status,
        "message": "NIDS Backend Server sẵn sàng!",
    }

# ==========================================
# CỔNG WEBSOCKET CHO REAL-TIME MONITORING
# ==========================================
@app.websocket("/ws/monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() # Chấp nhận kết nối từ Frontend
    print("Đã kết nối WebSocket với Frontend!")
    try:
        while True:
            # DỮ LIỆU TEST: Đẩy gói tin traffic mỗi giây để test biểu đồ React
            # Giàu (Backend) sẽ thay khối này bằng logic đọc gói tin thực tế từ Database
            traffic_data = {
                "type": "traffic",
                "payload": {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "packets": random.randint(5, 60) # Random số gói tin từ 5-60
                }
            }
            await websocket.send_json(traffic_data)
            await asyncio.sleep(1) # Đợi 1 giây rồi gửi tiếp
            
    except WebSocketDisconnect:
        print("Frontend đã ngắt kết nối WebSocket")