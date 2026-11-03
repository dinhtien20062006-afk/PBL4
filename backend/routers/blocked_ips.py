from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BlockedIP

router = APIRouter(prefix="/api/blocked-ips", tags=["Blocked IPs"])


class IPRequest(BaseModel):
    ip_address: str


class BlockRequest(BaseModel):
    ip_address: str
    reason: Optional[str] = "Chặn thủ công bởi Admin"
    alert_id: Optional[int] = None


def to_dict(b: BlockedIP) -> dict:
    return {
        "id": b.id,
        "alert_id": b.alert_id,
        "ip_address": b.ip_address,
        "reason": b.reason,
        "blocked_at": b.blocked_at.isoformat() if b.blocked_at else None,
        "unblocked_at": b.unblocked_at.isoformat() if b.unblocked_at else None,
        "status": b.status,
    }


@router.get("")
def get_active_blocked_ips(db: Session = Depends(get_db)):
    """Danh sách IP đang bị chặn (status = 'Blocked'), mới nhất trước."""
    rows = (
        db.query(BlockedIP)
        .filter(BlockedIP.status == "Blocked")
        .order_by(BlockedIP.blocked_at.desc(), BlockedIP.id.desc())
        .all()
    )
    return {"status": "success", "total": len(rows), "data": [to_dict(r) for r in rows]}


@router.post("")
def block_ip(req: BlockRequest, db: Session = Depends(get_db)):
    """Chặn một IP (ghi vào bảng blocked_ips)."""
    ip = req.ip_address.strip()
    if not ip:
        raise HTTPException(status_code=400, detail="ip_address không được để trống")

    existing = (
        db.query(BlockedIP)
        .filter(BlockedIP.ip_address == ip, BlockedIP.status == "Blocked")
        .first()
    )
    if existing:
        return {"status": "success", "message": f"IP {ip} đã bị chặn từ trước", "data": to_dict(existing)}

    row = BlockedIP(
        ip_address=ip,
        reason=req.reason,
        alert_id=req.alert_id,
        blocked_at=datetime.now(),
        status="Blocked",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "success", "message": f"Đã chặn IP {ip}", "data": to_dict(row)}


@router.post("/unblock")
def unblock_ip(req: IPRequest, db: Session = Depends(get_db)):
    """Gỡ chặn IP: status -> 'Unblocked', ghi unblocked_at."""
    rows = (
        db.query(BlockedIP)
        .filter(BlockedIP.ip_address == req.ip_address, BlockedIP.status == "Blocked")
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="IP không tồn tại hoặc đã được gỡ chặn")

    now = datetime.now()
    for r in rows:
        r.status = "Unblocked"
        r.unblocked_at = now
    db.commit()
    return {"status": "success", "message": f"Đã gỡ chặn IP {req.ip_address}"}
