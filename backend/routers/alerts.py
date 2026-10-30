from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import Database

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

class AlertCreate(BaseModel):
    rule_id: Optional[int] = None
    traffic_log_id: Optional[int] = None
    attack_type: str
    source_ip: str
    severity: Optional[str] = "High"

@router.post("/")
def create_alert(alert: AlertCreate):
    db = Database()
    conn = db.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database error")
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO alerts (rule_id, traffic_log_id, attack_type, source_ip, severity)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (alert.rule_id, alert.traffic_log_id, alert.attack_type, alert.source_ip, alert.severity)
        cursor.execute(query, values)
        conn.commit()
        return {"status": "success", "alert_id": cursor.lastrowid}
    finally:
        cursor.close()
        conn.close()

@router.get("/recent")
def get_recent_alerts(limit: int = 50):
    db = Database()
    conn = db.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database error")
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM alerts ORDER BY created_at DESC LIMIT %s"
        cursor.execute(query, (limit,))
        data = cursor.fetchall()
        return {"status": "success", "total": len(data), "data": data}
    finally:
        cursor.close()
        conn.close()