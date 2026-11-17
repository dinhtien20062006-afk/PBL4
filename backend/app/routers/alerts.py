from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlertHistory
from app.schemas import AlertCreate
from app.serializers import alert_to_dict
from app.ws_manager import manager

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.post("/trigger")
async def trigger_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """NIDS Engine gọi khi phát hiện tấn công -> lưu DB + đẩy realtime tới Dashboard."""
    try:
        row = AlertHistory(**alert.model_dump())
        db.add(row)
        db.commit()
        db.refresh(row)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    data = alert_to_dict(row)
    await manager.broadcast({"type": "new_alert", "data": data})
    return {"status": "success", "message": "Đã ghi nhận cảnh báo", "alert_id": row.id}


@router.get("")
def list_alerts(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.query(AlertHistory).order_by(AlertHistory.detected_at.desc()).limit(limit).all()
    return {"status": "success", "total": len(rows), "data": [alert_to_dict(r) for r in rows]}


@router.get("/recent", include_in_schema=False)
def list_alerts_compat(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    return list_alerts(limit, db)
