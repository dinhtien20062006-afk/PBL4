from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, TrafficLog

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


class AlertCreate(BaseModel):
    rule_id: Optional[int] = None
    traffic_log_id: Optional[int] = None
    attack_type: str
    source_ip: str
    severity: Optional[str] = "High"


def _query_alerts(db: Session, limit: int):
    # LEFT JOIN traffic_logs để lấy cổng bị tấn công (bảng alerts không có cột port)
    rows = (
        db.query(Alert, TrafficLog.port)
        .outerjoin(TrafficLog, Alert.traffic_log_id == TrafficLog.id)
        .order_by(Alert.created_at.desc(), Alert.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": a.id,
            "rule_id": a.rule_id,
            "traffic_log_id": a.traffic_log_id,
            "attack_type": a.attack_type,
            "source_ip": a.source_ip,
            "severity": a.severity,
            "port": port,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a, port in rows
    ]


@router.get("")
def list_alerts(limit: int = 100, db: Session = Depends(get_db)):
    data = _query_alerts(db, limit)
    return {"status": "success", "total": len(data), "data": data}


@router.get("/recent")
def get_recent_alerts(limit: int = 50, db: Session = Depends(get_db)):
    data = _query_alerts(db, limit)
    return {"status": "success", "total": len(data), "data": data}


@router.post("")
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    row = Alert(**alert.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "success", "alert_id": row.id}
