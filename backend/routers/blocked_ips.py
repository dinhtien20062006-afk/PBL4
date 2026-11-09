import asyncio
import ipaddress
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pydantic import field_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.firewall import block_ip as firewall_block_ip
from app.firewall import is_ip_blocked as firewall_is_ip_blocked
from app.firewall import unblock_ip as firewall_unblock_ip
from app.models import BlockedIP
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
    alert_id: int | None = None

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        return str(ipaddress.ip_address(value))


@router.get("/")
def get_active_blocked_ips(db: Session = Depends(get_db)):
    """Truy vấn toàn bộ danh sách IP đang bị chặn (status == "Blocked")"""
    ips = db.query(BlockedIP).filter(BlockedIP.status == "Blocked").all()
    return {"status": "success", "data": ips}

@router.post("/")
async def block_ip(req: BlockRequest, db: Session = Depends(get_db)):
    existing = db.query(BlockedIP).filter(
        BlockedIP.ip_address == req.ip_address,
        BlockedIP.status == "Blocked",
    ).first()
    was_blocked = await asyncio.to_thread(firewall_is_ip_blocked, req.ip_address)
    firewall_updated = await asyncio.to_thread(firewall_block_ip, req.ip_address)
    if not firewall_updated:
        raise HTTPException(
            status_code=503,
            detail=(
                "Không thể chặn IP trên Windows Firewall. Hãy chạy backend bằng "
                "quyền Administrator và kiểm tra Windows Defender Firewall."
            ),
        )
    if existing:
        return {"status": "success", "message": f"IP {req.ip_address} đã bị chặn", "id": existing.id}

    blocked_ip = BlockedIP(
        ip_address=req.ip_address,
        reason=req.reason,
        alert_id=req.alert_id,
        status="Blocked",
    )
    db.add(blocked_ip)
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        if not was_blocked:
            restored = await asyncio.to_thread(firewall_unblock_ip, req.ip_address)
            if not restored:
                logger.error(
                    "Failed to commit block for %s and failed to remove its firewall rule",
                    req.ip_address,
                    exc_info=True,
                )
        raise HTTPException(
            status_code=500,
            detail="Không thể lưu trạng thái chặn IP vào MySQL.",
        ) from exc
    db.refresh(blocked_ip)
    await manager.broadcast(
        {
            "type": "ip_blocked",
            "data": {"ip_address": req.ip_address, "status": "Blocked"},
        }
    )
    return {"status": "success", "message": f"Đã chặn IP {req.ip_address}", "id": blocked_ip.id}


async def _unblock_ip(req: UnblockRequest, db: Session) -> dict:
    blocked_ip = db.query(BlockedIP).filter(
        BlockedIP.ip_address == req.ip_address,
        BlockedIP.status == "Blocked",
    ).first()
    if not blocked_ip:
        raise HTTPException(status_code=404, detail="IP không tồn tại hoặc đã được gỡ chặn")

    firewall_updated = await asyncio.to_thread(firewall_unblock_ip, req.ip_address)
    if not firewall_updated:
        raise HTTPException(
            status_code=503,
            detail=(
                "Không thể gỡ IP khỏi Windows Firewall. Hãy kiểm tra rule "
                "NIDS_Blacklist_Rule và chạy backend bằng quyền Administrator."
            ),
        )

    blocked_ip.status = "0"
    blocked_ip.unblocked_at = datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        restored = await asyncio.to_thread(firewall_block_ip, req.ip_address)
        if not restored:
            logger.error(
                "Failed to commit unblock for %s and failed to restore its firewall block",
                req.ip_address,
                exc_info=True,
            )
            detail = (
                "MySQL update failed and Windows Firewall rollback also failed. "
                "Verify the firewall rule manually."
            )
        else:
            detail = "MySQL update failed; the Windows Firewall block was restored."
        raise HTTPException(
            status_code=500,
            detail=detail,
        ) from exc

    event = {
        "type": "ip_unblocked",
        "data": {"ip_address": req.ip_address, "status": 0},
    }
    await manager.broadcast(event)
    return {
        "status": "success",
        "message": f"Đã gỡ chặn IP {req.ip_address}",
        "data": event["data"],
    }


@router.post("/unblock")
async def unblock_ip(req: UnblockRequest, db: Session = Depends(get_db)):
    """Gỡ IP khỏi Windows Firewall, cập nhật MySQL và phát sự kiện WebSocket."""
    return await _unblock_ip(req, db)


@unblock_router.post("/api/unblock")
async def unblock_ip_compat(req: UnblockRequest, db: Session = Depends(get_db)):
    """Alias tương thích với endpoint POST /api/unblock trong yêu cầu."""
    return await _unblock_ip(req, db)