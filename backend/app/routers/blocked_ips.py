import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import firewall
from app.config import FIREWALL_ENABLED
from app.database import SessionLocal, get_db
from app.models import BlacklistIP
from app.schemas import BlockRequest, IpRequest
from app.serializers import blocked_to_dict
from app.ws_manager import manager

router = APIRouter(prefix="/api/blocked-ips", tags=["Blocked IPs"])
compat_router = APIRouter(tags=["Blocked IPs"])
logger = logging.getLogger(__name__)


async def _fw(func, ip: str) -> bool:
    """Chạy lệnh Windows Firewall ở thread riêng; bỏ qua khi FIREWALL_ENABLED=false."""
    if not FIREWALL_ENABLED:
        return True
    return await asyncio.to_thread(func, ip)


def _active(db: Session, ip: str):
    return (
        db.query(BlacklistIP)
        .filter(BlacklistIP.ip_address == ip, BlacklistIP.status_active.is_(True))
        .first()
    )


@router.get("")
def list_blocked(db: Session = Depends(get_db)):
    rows = (
        db.query(BlacklistIP)
        .filter(BlacklistIP.status_active.is_(True))
        .order_by(BlacklistIP.created_at.desc())
        .all()
    )
    return {"status": "success", "total": len(rows), "data": [blocked_to_dict(r) for r in rows]}


def _firewall_in_background(func, undo, ip: str, undo_event: str):
    """Chạy Firewall ngầm để API trả lời ngay. Lỗi -> hoàn tác DB và báo giao diện nạp lại."""

    async def task():
        if await _fw(func, ip):
            return
        logger.error("Firewall thất bại cho %s, hoàn tác CSDL", ip)
        with SessionLocal() as db:
            undo(db, ip)
            db.commit()
        await manager.broadcast({"type": undo_event, "data": {"ip_address": ip}})

    asyncio.create_task(task())


def _undo_block(db: Session, ip: str):
    for row in db.query(BlacklistIP).filter(BlacklistIP.ip_address == ip, BlacklistIP.status_active.is_(True)):
        row.status_active = False
        row.unblocked_at = datetime.now()


def _undo_unblock(db: Session, ip: str):
    row = (
        db.query(BlacklistIP)
        .filter(BlacklistIP.ip_address == ip, BlacklistIP.status_active.is_(False))
        .order_by(BlacklistIP.id.desc())
        .first()
    )
    if row:
        row.status_active = True
        row.unblocked_at = None


@router.post("")
async def block_ip(req: BlockRequest, db: Session = Depends(get_db)):
    existing = _active(db, req.ip_address)
    if existing:
        return {"status": "success", "message": f"IP {req.ip_address} đã bị chặn", "id": existing.id}

    row = BlacklistIP(ip_address=req.ip_address, reason_blocked=req.reason, status_active=True)
    db.add(row)
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(500, "Lỗi ghi CSDL.") from exc

    db.refresh(row)
    _firewall_in_background(firewall.block_ip, _undo_block, req.ip_address, "ip_unblocked")
    await manager.broadcast({"type": "ip_blocked", "data": blocked_to_dict(row)})
    return {"status": "success", "message": f"Đã chặn IP {req.ip_address}", "id": row.id}


async def _unblock(req: IpRequest, db: Session) -> dict:
    row = _active(db, req.ip_address)
    if not row:
        raise HTTPException(404, "IP không tồn tại hoặc đã được gỡ chặn")

    row.status_active = False
    row.unblocked_at = datetime.now()
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(500, "Lỗi ghi CSDL.") from exc

    _firewall_in_background(firewall.unblock_ip, _undo_unblock, req.ip_address, "ip_blocked")
    await manager.broadcast({"type": "ip_unblocked", "data": {"ip_address": req.ip_address}})
    return {"status": "success", "message": f"Đã gỡ chặn IP {req.ip_address}"}


@router.post("/unblock")
async def unblock_ip(req: IpRequest, db: Session = Depends(get_db)):
    return await _unblock(req, db)


@compat_router.post("/api/unblock", include_in_schema=False)
async def unblock_ip_compat(req: IpRequest, db: Session = Depends(get_db)):
    return await _unblock(req, db)
