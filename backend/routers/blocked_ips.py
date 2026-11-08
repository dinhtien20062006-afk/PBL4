from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import BlockedIP

router = APIRouter(prefix="/api/blocked-ips", tags=["Blocked IPs"])

class UnblockRequest(BaseModel):
    ip_address: str

class BlockRequest(BaseModel):
    ip_address: str
    reason: str | None = None
    alert_id: int | None = None

@router.get("/")
def get_active_blocked_ips(db: Session = Depends(get_db)):
    """Truy vấn toàn bộ danh sách IP đang bị chặn (status == "Blocked")"""
    ips = db.query(BlockedIP).filter(BlockedIP.status == "Blocked").all()
    return {"status": "success", "data": ips}

@router.post("/")
def block_ip(req: BlockRequest, db: Session = Depends(get_db)):
    existing = db.query(BlockedIP).filter(
        BlockedIP.ip_address == req.ip_address,
        BlockedIP.status == "Blocked",
    ).first()
    if existing:
        return {"status": "success", "message": f"IP {req.ip_address} đã bị chặn", "id": existing.id}

    blocked_ip = BlockedIP(
        ip_address=req.ip_address,
        reason=req.reason,
        alert_id=req.alert_id,
        status="Blocked",
    )
    db.add(blocked_ip)
    db.commit()
    db.refresh(blocked_ip)
    return {"status": "success", "message": f"Đã chặn IP {req.ip_address}", "id": blocked_ip.id}

@router.post("/unblock")
def unblock_ip(req: UnblockRequest, db: Session = Depends(get_db)):
    """Tiếp nhận yêu cầu gỡ chặn IP và cập nhật DB (status == "Unblocked")"""
    blocked_ip = db.query(BlockedIP).filter(
        BlockedIP.ip_address == req.ip_address, 
        BlockedIP.status == "Blocked"
    ).first()
    
    if not blocked_ip:
        raise HTTPException(status_code=404, detail="IP không tồn tại hoặc đã được gỡ chặn")
        
    blocked_ip.status = "Unblocked"
    blocked_ip.unblocked_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": f"Đã gỡ chặn IP {req.ip_address}"}