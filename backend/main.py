from fastapi import FastAPI, HTTPException
from database import Database

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="PBL4 Mail NIDS API")

# Endpoint 1: Kiểm tra trạng thái Server
@app.get("/")
def read_root():
    return {
        "project": "PBL4 - Mail NIDS",
        "message": "Backend server is running correctly",
        "status": "success"
    }

# Endpoint 2: Kiểm tra cấu hình kết nối Database
@app.get("/api/test-db")
def test_db_connection():
    db = Database()
    conn = db.connect()
    
    if conn and conn.is_connected():
        db.disconnect()
        return {
            "database": db.database,
            "status": "connected",
            "message": "Kết nối MySQL thành công"
        }
    else:
        raise HTTPException(status_code=500, detail="Không thể kết nối đến Cơ sở dữ liệu")