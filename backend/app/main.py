from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
