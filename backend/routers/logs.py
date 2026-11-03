from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TrafficLog

router = APIRouter(prefix="/api/logs", tags=["Traffic Logs"])


class TrafficLogCreate(BaseModel):
    source_ip: str
    dest_ip: str
    port: Optional[int] = None
    protocol: Optional[str] = None
    packet_size: Optional[int] = None
    status: Optional[str] = "Normal"


def to_dict(l: TrafficLog) -> dict:
    return {
        "id": l.id,
        "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        "source_ip": l.source_ip,
        "dest_ip": l.dest_ip,
        "port": l.port,
        "protocol": l.protocol,
        "packet_size": l.packet_size,
        "status": l.status,
    }


@router.get("")
def get_all_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(TrafficLog).order_by(TrafficLog.timestamp.desc(), TrafficLog.id.desc()).limit(limit).all()
    return {"status": "success", "total": len(logs), "data": [to_dict(l) for l in logs]}


@router.post("/ingest")
def ingest_log(log: TrafficLogCreate, db: Session = Depends(get_db)):
    """Nhận gói tin từ NIDS Engine và lưu vào MySQL."""
    try:
        new_log = TrafficLog(**log.model_dump())
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return {"status": "success", "message": "Đã lưu log", "log_id": new_log.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
def get_recent_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(TrafficLog).order_by(TrafficLog.timestamp.desc(), TrafficLog.id.desc()).limit(limit).all()
    return {"status": "success", "total": len(logs), "data": [to_dict(l) for l in logs]}
