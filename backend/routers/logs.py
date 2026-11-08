from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TrafficLog

router = APIRouter(
    prefix="/api/logs",
    tags=["Traffic Logs"]
)

class TrafficLogCreate(BaseModel):
    source_ip: str
    dest_ip: str
    port: Optional[int] = None
    protocol: Optional[str] = None
    packet_size: Optional[int] = None
    status: Optional[str] = "Normal"

@router.get("/")
def get_all_logs(limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách log thực tế từ CSDL MySQL"""
    logs = db.query(TrafficLog).order_by(TrafficLog.timestamp.desc()).limit(limit).all()
    return {"status": "success", "data": logs}

@router.post("/traffic")
def ingest_log(log: TrafficLogCreate, db: Session = Depends(get_db)):
    """Nhận dữ liệu gói tin từ NIDS Engine và lưu vào MySQL bằng ORM"""
    try:
        new_log = TrafficLog(**log.model_dump()) 
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return {"status": "success", "message": "Đã lưu log", "log_id": new_log.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
def ingest_log_compat(log: TrafficLogCreate, db: Session = Depends(get_db)):
    return ingest_log(log, db)

@router.get("/recent")
def get_recent_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Trả về danh sách gói tin mới nhất (dùng cho realtime Dashboard)"""
    logs = db.query(TrafficLog).order_by(TrafficLog.timestamp.desc()).limit(limit).all()
    return {"status": "success", "total": len(logs), "data": logs}