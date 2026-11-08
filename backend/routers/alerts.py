from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert, TrafficLog
from app.ws_manager import manager

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

class AlertCreate(BaseModel):
    rule_id: Optional[int] = None
    traffic_log_id: Optional[int] = None
    attack_type: str
    source_ip: str
    severity: Optional[str] = "High"

@router.post("/trigger")
async def trigger_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """API nhận thông tin cảnh báo khi Core NIDS phát hiện dấu hiệu tấn công"""
    try:
        # Hỗ trợ cả Pydantic V1 (dict) và V2 (model_dump)
        alert_data = alert.model_dump() if hasattr(alert, 'model_dump') else alert.dict()
        new_alert = Alert(**alert_data)
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
    """Trả về danh sách cảnh báo mới nhất"""
    alerts = (
        db.query(Alert, TrafficLog.port)
        .outerjoin(TrafficLog, Alert.traffic_log_id == TrafficLog.id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )
    data = [
        {
            "id": alert.id,
            "rule_id": alert.rule_id,
            "traffic_log_id": alert.traffic_log_id,
            "attack_type": alert.attack_type,
            "source_ip": alert.source_ip,
            "severity": alert.severity,
            "created_at": alert.created_at,
            "port": port,
        }
        for alert, port in alerts
    ]
    return {"status": "success", "total": len(data), "data": data}


@router.get("/recent")
def get_recent_alerts_compat(limit: int = 50, db: Session = Depends(get_db)):
    return get_recent_alerts(limit, db)