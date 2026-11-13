from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AlertHistory
from app.schemas import AlertCreate
from app.ws_manager import manager

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.post("/trigger")
async def trigger_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    try:
        alert_data = alert.model_dump() if hasattr(alert, 'model_dump') else alert.dict()
        new_alert = AlertHistory(**alert_data)
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        await manager.broadcast({
            "type": "new_alert",
            "data": alert_data
        })
        return {"status": "success", "message": "Đã ghi nhận cảnh báo", "alert_id": new_alert.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_recent_alerts(limit: int = 50, db: Session = Depends(get_db)):
    alerts = db.query(AlertHistory).order_by(AlertHistory.detected_at.desc()).limit(limit).all()
    # Cấu trúc trả về vẫn giữ key cũ để Frontend không bị lỗi hiển thị
    data = [
        {
            "id": alert.id,
            "source_ip": alert.ip_source,
            "attack_type": alert.attack_type,
            "severity": alert.severity,
            "created_at": alert.detected_at,
            "threshold_value": alert.threshold_value
        }
        for alert in alerts
    ]
    return {"status": "success", "total": len(data), "data": data}

@router.get("/recent")
def get_recent_alerts_compat(limit: int = 50, db: Session = Depends(get_db)):
    return get_recent_alerts(limit, db)