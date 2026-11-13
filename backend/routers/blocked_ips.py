import asyncio
import ipaddress
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.firewall import block_ip as firewall_block_ip
from app.firewall import is_ip_blocked as firewall_is_ip_blocked
from app.firewall import unblock_ip as firewall_unblock_ip
from app.models import BlacklistIP
from app.ws_manager import manager

router = APIRouter(prefix="/api/blocked-ips", tags=["Blocked IPs"])
unblock_router = APIRouter(tags=["Blocked IPs"])
logger = logging.getLogger(__name__)

class UnblockRequest(BaseModel):
    ip_address: str
    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        return str(ipaddress.ip_address(value))

class BlockRequest(BaseModel):
    ip_address: str
    reason: str | None = None

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        return str(ipaddress.ip_address(value))

@router.get("/")
def get_active_blocked_ips(db: Session = Depends(get_db)):
    ips = db.query(BlacklistIP).filter(BlacklistIP.status_active == True).all()
    data = [
        {
            "id": ip.id,
            "ip_address": ip.ip_address,
            "reason": ip.reason_blocked,
            "blocked_at": ip.created_at,
            "status": "Blocked" if ip.status_active else "0"
        }
        for ip in ips
    ]
    return {"status": "success", "data": data}

@router.post("/")
async def block_ip(req: BlockRequest, db: Session = Depends(get_db)):
    existing = db.query(BlacklistIP).filter(
        BlacklistIP.ip_address == req.ip_address,
        BlacklistIP.status_active == True,
    ).first()
    was_blocked = await asyncio.to_thread(firewall_is_ip_blocked, req.ip_address)
    firewall_updated = await asyncio.to_thread(firewall_block_ip, req.ip_address)
    
    if not firewall_updated:
        raise HTTPException(status_code=503, detail="Không thể chặn IP trên Windows Firewall.")
    if existing:
        return {"status": "success", "message": f"IP {req.ip_address} đã bị chặn", "id": existing.id}

    blocked_ip = BlacklistIP(
        ip_address=req.ip_address,
        reason_blocked=req.reason,
        status_active=True,
    )
    db.add(blocked_ip)
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        if not was_blocked:
            await asyncio.to_thread(firewall_unblock_ip, req.ip_address)
        raise HTTPException(status_code=500, detail="Lỗi DB.") from exc
        
    db.refresh(blocked_ip)
    await manager.broadcast({
        "type": "ip_blocked",
        "data": {"ip_address": req.ip_address, "status": "Blocked"},
    })
    return {"status": "success", "message": f"Đã chặn IP {req.ip_address}", "id": blocked_ip.id}

async def _unblock_ip(req: UnblockRequest, db: Session) -> dict:
    blocked_ip = db.query(BlacklistIP).filter(
        BlacklistIP.ip_address == req.ip_address,
        BlacklistIP.status_active == True,
    ).first()
    if not blocked_ip:
        raise HTTPException(status_code=404, detail="IP không tồn tại hoặc đã gỡ chặn")

    firewall_updated = await asyncio.to_thread(firewall_unblock_ip, req.ip_address)
    if not firewall_updated:
        raise HTTPException(status_code=503, detail="Lỗi gỡ IP trên Firewall.")

    blocked_ip.status_active = False
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        await asyncio.to_thread(firewall_block_ip, req.ip_address)
        raise HTTPException(status_code=500, detail="Lỗi DB.") from exc

    event = {"type": "ip_unblocked", "data": {"ip_address": req.ip_address, "status": 0}}
    await manager.broadcast(event)
    return {"status": "success", "message": f"Đã gỡ chặn IP {req.ip_address}", "data": event["data"]}

@router.post("/unblock")
async def unblock_ip(req: UnblockRequest, db: Session = Depends(get_db)):
    return await _unblock_ip(req, db)

@unblock_router.post("/api/unblock")
async def unblock_ip_compat(req: UnblockRequest, db: Session = Depends(get_db)):
    return await _unblock_ip(req, db)