from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LogTraffic
from app.schemas import TrafficLogCreate

router = APIRouter(prefix="/api/logs", tags=["Traffic Logs"])

@router.get("/")
def get_all_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(LogTraffic).order_by(LogTraffic.timestamp.desc()).limit(limit).all()
    return {"status": "success", "data": logs}

@router.post("/traffic")
def ingest_log(log: TrafficLogCreate, db: Session = Depends(get_db)):
    try:
        new_log = LogTraffic(**log.model_dump()) 
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
    logs = db.query(LogTraffic).order_by(LogTraffic.timestamp.desc()).limit(limit).all()
    return {"status": "success", "total": len(logs), "data": logs}