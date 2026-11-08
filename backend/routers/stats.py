from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, BlockedIP, TrafficLog

router = APIRouter(tags=["Dashboard Statistics"])


def _since(minutes: int) -> datetime:
    return datetime.utcnow() - timedelta(minutes=minutes)


@router.get("/api/ips")
def get_ips(db: Session = Depends(get_db)):
    blocked = {
        ip for (ip,) in db.query(BlockedIP.ip_address).filter(BlockedIP.status == "Blocked").all()
    }
    rows = (
        db.query(
            TrafficLog.source_ip.label("ip"),
            func.count(TrafficLog.id).label("packets"),
            func.max(TrafficLog.timestamp).label("last_seen"),
            func.max(TrafficLog.protocol).label("proto"),
        )
        .group_by(TrafficLog.source_ip)
        .order_by(desc("last_seen"))
        .all()
    )
    return {
        "status": "success",
        "data": [
            {
                "ip": row.ip,
                "status": "blocked" if row.ip in blocked else "normal",
                "proto": row.proto,
                "packets": row.packets,
                "last_seen": row.last_seen,
                "blocked": row.ip in blocked,
            }
            for row in rows
        ],
    }


@router.get("/api/stats/overview")
def get_overview(db: Session = Depends(get_db)):
    total_packets = db.query(func.count(TrafficLog.id)).scalar() or 0
    alerts_total = db.query(func.count(Alert.id)).scalar() or 0
    recent_count = (
        db.query(func.count(TrafficLog.id))
        .filter(TrafficLog.timestamp >= _since(1))
        .scalar()
        or 0
    )
    return {
        "status": "success",
        "data": {
            "packets_per_second": round(recent_count / 60, 2),
            "packets_last_minute": recent_count,
            "alerts_total": alerts_total,
            "total_packets": total_packets,
        },
    }


@router.get("/api/stats/traffic")
def get_traffic(minutes: int = Query(30, ge=1, le=1440), db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.date_format(TrafficLog.timestamp, "%Y-%m-%d %H:%i").label("time"),
            func.count(TrafficLog.id).label("packets"),
        )
        .filter(TrafficLog.timestamp >= _since(minutes))
        .group_by("time")
        .order_by("time")
        .all()
    )
    return {"status": "success", "data": [{"time": row.time, "packets": row.packets} for row in rows]}


@router.get("/api/stats/protocols")
def get_protocols(db: Session = Depends(get_db)):
    total = db.query(func.count(TrafficLog.id)).scalar() or 0
    rows = (
        db.query(TrafficLog.protocol.label("label"), func.count(TrafficLog.id).label("count"))
        .filter(TrafficLog.timestamp >= _since(60))
        .group_by(TrafficLog.protocol)
        .all()
    )
    return {
        "status": "success",
        "data": [
            {"label": row.label or "Unknown", "value": round(row.count * 100 / total, 2) if total else 0}
            for row in rows
        ],
    }


@router.get("/api/stats/ports")
def get_ports(db: Session = Depends(get_db)):
    rows = (
        db.query(TrafficLog.port.label("port"), func.count(TrafficLog.id).label("count"))
        .filter(TrafficLog.timestamp >= _since(60))
        .group_by(TrafficLog.port)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    return {"status": "success", "data": [{"label": str(row.port or "Unknown"), "value": row.count} for row in rows]}


@router.get("/api/stats/top-sources")
def get_top_sources(limit: int = Query(5, ge=1, le=100), db: Session = Depends(get_db)):
    rows = (
        db.query(TrafficLog.source_ip.label("ip"), func.count(TrafficLog.id).label("packets"))
        .group_by(TrafficLog.source_ip)
        .order_by(desc("packets"))
        .limit(limit)
        .all()
    )
    blocked = {
        ip for (ip,) in db.query(BlockedIP.ip_address).filter(BlockedIP.status == "Blocked").all()
    }
    return {
        "status": "success",
        "data": [
            {
                "ip": row.ip,
                "packets": row.packets,
                "blocked": row.ip in blocked,
                "status": "blocked" if row.ip in blocked else "normal",
            }
            for row in rows
        ],
    }