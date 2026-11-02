# from fastapi import FastAPI
# from routers.logs import router as logs_router 
# from routers.alerts import router as alerts_router
# from database import Database
# from routers import alerts

# app = FastAPI(
#     title="PBL4 Mail NIDS API",
#     description="Restful API Base với cấu trúc Router và Connection Pool",
#     version="1.1.0"
# )

# # Đăng ký Router
# app.include_router(logs_router)
# app.include_router(alerts_router)

# @app.get("/", tags=["Health Check"])
# def health_check():
#     """Hàm kiểm tra trạng thái hoạt động của Server và Database"""
#     db = Database()
#     db_status = db.check_db_status()
    
#     return {
#         "api_status": "OK",
#         "database_connected": db_status,
#         "message": "NIDS Backend Server sẵn sàng!"
#     }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.logs import router as logs_router 
from routers.alerts import router as alerts_router
from app.database import Database
from routers.blocked_ips import router as blocked_ips_router
# 1. Khởi tạo app đầu tiên
app = FastAPI(
    title="PBL4 Mail NIDS API",
    description="RESTful API Base với cấu trúc Router và Connection Pool",
    version="1.1.0"
)

# 2. Cấu hình CORS (Xử lý lỗi chặn tên miền cho Frontend của Quyền)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Đăng ký các Router
app.include_router(logs_router)
app.include_router(alerts_router)
app.include_router(blocked_ips_router)

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