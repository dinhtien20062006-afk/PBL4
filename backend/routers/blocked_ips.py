from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import BlockedIP

router = APIRouter(prefix="/api/blocked-ips", tags=["Blocked IPs"])

class UnblockRequest(BaseModel):
    ip_address: str

@router.get("/")
def get_active_blocked_ips(db: Session = Depends(get_db)):
    """Truy vấn toàn bộ danh sách IP đang bị chặn (status == "Blocked")"""
    ips = db.query(BlockedIP).filter(BlockedIP.status == "Blocked").all()
    return {"status": "success", "data": ips}

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
    db.commit()
    return {"status": "success", "message": f"Đã gỡ chặn IP {req.ip_address}"}