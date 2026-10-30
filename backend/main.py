from fastapi import FastAPI
from routers.logs import router as logs_router 
from database import Database
from routers import alerts
app.include_router(alerts.router)

app = FastAPI(
    title="PBL4 Mail NIDS API",
    description="Restful API Base với cấu trúc Router và Connection Pool",
    version="1.1.0"
)

# Đăng ký Router
app.include_router(logs_router)

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