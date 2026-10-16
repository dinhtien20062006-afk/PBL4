from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import Database

# Khởi tạo Router cho Logs
router = APIRouter(
    prefix="/api/logs",
    tags=["Traffic Logs"]
)

# Khai báo cấu trúc JSON (Schema) khi NIDS gửi log lên
class TrafficLogCreate(BaseModel):
    source_ip: str
    dest_ip: str
    port: Optional[int] = None
    protocol: Optional[str] = None
    packet_size: Optional[int] = None
    status: Optional[str] = "Normal"

@router.post("/ingest")
def ingest_log(log: TrafficLogCreate):
    """Nhận dữ liệu gói tin từ NIDS Engine và lưu vào MySQL"""
    db = Database()
    conn = db.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database error")
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO traffic_logs (source_ip, dest_ip, port, protocol, packet_size, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (log.source_ip, log.dest_ip, log.port, log.protocol, log.packet_size, log.status)
        cursor.execute(query, values)
        conn.commit() # Xác nhận lưu vào CSDL
        return {"status": "success", "message": "Đã lưu log", "log_id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close() # Rất quan trọng: Trả kết nối về Pool

@router.get("/recent")
def get_recent_logs(limit: int = 50):
    """Trả về danh sách gói tin mới nhất (dùng cho realtime Dashboard)"""
    db = Database()
    conn = db.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database error")
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM traffic_logs ORDER BY timestamp DESC LIMIT %s"
        cursor.execute(query, (limit,))
        data = cursor.fetchall()
        return {"status": "success", "total": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()