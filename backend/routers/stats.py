from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, BlockedIP, TrafficLog

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    now = datetime.now()
    last_minute = (
        db.query(func.count(TrafficLog.id))
        .filter(TrafficLog.timestamp >= now - timedelta(seconds=60))
        .scalar()
    )
    return {
        "status": "success",
        "data": {
            "packets_per_second": round((last_minute or 0) / 60, 2),
            "packets_last_minute": last_minute or 0,
            "total_packets": db.query(func.count(TrafficLog.id)).scalar() or 0,
            "alerts_total": db.query(func.count(Alert.id)).scalar() or 0,
            "blocked_ips": db.query(func.count(BlockedIP.id)).filter(BlockedIP.status == "Blocked").scalar() or 0,
        },
    }


@router.get("/traffic")
def traffic_series(minutes: int = 30, db: Session = Depends(get_db)):
    """Số gói tin theo từng phút trong `minutes` phút gần nhất (điền 0 cho phút trống)."""
    now = datetime.now().replace(second=0, microsecond=0)
    start = now - timedelta(minutes=minutes - 1)
    bucket = func.date_format(TrafficLog.timestamp, "%Y-%m-%d %H:%i:00")
    rows = (
        db.query(bucket, func.count(TrafficLog.id))
        .filter(TrafficLog.timestamp >= start)
        .group_by(bucket)
        .all()
    )
    counts = {r[0]: r[1] for r in rows}
    data = []
    for i in range(minutes):
        t = start + timedelta(minutes=i)
        data.append({"t": t.isoformat(), "packets": counts.get(t.strftime("%Y-%m-%d %H:%M:00"), 0)})
    return {"status": "success", "data": data}


@router.get("/protocols")
def protocols(minutes: int = 60, db: Session = Depends(get_db)):
    since = datetime.now() - timedelta(minutes=minutes)
    rows = (
        db.query(TrafficLog.protocol, func.count(TrafficLog.id))
        .filter(TrafficLog.timestamp >= since)
        .group_by(TrafficLog.protocol)
        .order_by(func.count(TrafficLog.id).desc())
        .all()
    )
    total = sum(r[1] for r in rows) or 1
    return {
        "status": "success",
        "data": [
            {"label": r[0] or "Khác", "count": r[1], "value": round(r[1] * 100 / total)}
            for r in rows
        ],
    }


@router.get("/ports")
def ports(minutes: int = 60, db: Session = Depends(get_db)):
    since = datetime.now() - timedelta(minutes=minutes)
    base = db.query(func.count(TrafficLog.id)).filter(TrafficLog.timestamp >= since)
    smtp = base.filter(TrafficLog.port == 25).scalar() or 0
    pop3 = (
        db.query(func.count(TrafficLog.id))
        .filter(TrafficLog.timestamp >= since, TrafficLog.port == 110)
        .scalar()
        or 0
    )
    total = (
        db.query(func.count(TrafficLog.id)).filter(TrafficLog.timestamp >= since).scalar() or 0
    )
    return {
        "status": "success",
        "data": [
            {"label": "SMTP · 25", "value": smtp},
            {"label": "POP3 · 110", "value": pop3},
            {"label": "Khác", "value": max(total - smtp - pop3, 0)},
        ],
    }


@router.get("/top-sources")
def top_sources(limit: int = 5, minutes: int = 60, db: Session = Depends(get_db)):
    since = datetime.now() - timedelta(minutes=minutes)
    rows = (
        db.query(TrafficLog.source_ip, func.count(TrafficLog.id))
        .filter(TrafficLog.timestamp >= since)
        .group_by(TrafficLog.source_ip)
        .order_by(func.count(TrafficLog.id).desc())
        .limit(limit)
        .all()
    )
    blocked = {
        r[0] for r in db.query(BlockedIP.ip_address).filter(BlockedIP.status == "Blocked").all()
    }
    alerted = {r[0] for r in db.query(Alert.source_ip).distinct().all()}
    return {
        "status": "success",
        "data": [
            {
                "ip": ip,
                "packets": n,
                "blocked": ip in blocked,
                "status": "suspicious" if ip in alerted else "normal",
            }
            for ip, n in rows
        ],
    }
