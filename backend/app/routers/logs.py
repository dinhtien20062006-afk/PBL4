from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LogTraffic
from app.schemas import TrafficBatch, TrafficLogCreate
from app.serializers import log_to_dict

router = APIRouter(prefix="/api/logs", tags=["Traffic Logs"])


@router.get("")
def list_logs(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    rows = db.query(LogTraffic).order_by(LogTraffic.id.desc()).limit(limit).all()
    return {"status": "success", "total": len(rows), "data": [log_to_dict(r) for r in rows]}


@router.get("/recent")
def recent_logs(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    return list_logs(limit, db)


@router.post("/traffic")
def ingest_log(log: TrafficLogCreate, db: Session = Depends(get_db)):
    """NIDS Engine gửi thống kê gói tin theo từng IP nguồn."""
    try:
        row = LogTraffic(**log.model_dump())
        db.add(row)
        db.commit()
        db.refresh(row)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "success", "message": "Đã lưu log", "log_id": row.id}


@router.post("/traffic/batch")
def ingest_batch(batch: TrafficBatch, db: Session = Depends(get_db)):
    """Ghi nhiều bản ghi trong 1 transaction (1 commit thay vì hàng trăm)."""
    if not batch.items:
        return {"status": "success", "inserted": 0}
    try:
        db.add_all([LogTraffic(**item.model_dump()) for item in batch.items])
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "success", "inserted": len(batch.items)}


@router.post("/ingest", include_in_schema=False)
def ingest_log_compat(log: TrafficLogCreate, db: Session = Depends(get_db)):
    return ingest_log(log, db)
