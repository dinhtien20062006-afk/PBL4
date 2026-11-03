from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

class AlertCreate(BaseModel):
    rule_id: Optional[int] = None
    traffic_log_id: Optional[int] = None
    attack_type: str
    source_ip: str
    severity: Optional[str] = "High"

@router.post("/trigger")
def trigger_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """API nhận thông tin cảnh báo khi Core NIDS phát hiện dấu hiệu tấn công"""
    try:
        # Hỗ trợ cả Pydantic V1 (dict) và V2 (model_dump)
        alert_data = alert.model_dump() if hasattr(alert, 'model_dump') else alert.dict()
        new_alert = Alert(**alert_data)
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        return {"status": "success", "message": "Đã ghi nhận cảnh báo", "alert_id": new_alert.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
def get_recent_alerts(limit: int = 50, db: Session = Depends(get_db)):
    """Trả về danh sách cảnh báo mới nhất"""
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()
    return {"status": "success", "total": len(alerts), "data": alerts}