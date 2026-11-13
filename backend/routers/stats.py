from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AlertHistory, BlacklistIP, LogTraffic

router = APIRouter(tags=["Dashboard Statistics"])

def _since(minutes: int) -> datetime:
    return datetime.utcnow() - timedelta(minutes=minutes)

@router.get("/api/ips")
def get_ips(db: Session = Depends(get_db)):
    blocked = {
        ip for (ip,) in db.query(BlacklistIP.ip_address).filter(BlacklistIP.status_active == True).all()
    }
    rows = (
        db.query(
            LogTraffic.ip_source.label("ip"),
            func.count(LogTraffic.id).label("packets"),
            func.max(LogTraffic.timestamp).label("last_seen"),
            func.max(LogTraffic.protocol).label("proto"),
        )
        .group_by(LogTraffic.ip_source)
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
    total_packets = db.query(func.count(LogTraffic.id)).scalar() or 0
    alerts_total = db.query(func.count(AlertHistory.id)).scalar() or 0
    recent_count = (
        db.query(func.count(LogTraffic.id))
        .filter(LogTraffic.timestamp >= _since(1))
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
            func.date_format(LogTraffic.timestamp, "%Y-%m-%d %H:%i").label("time"),
            func.count(LogTraffic.id).label("packets"),
        )
        .filter(LogTraffic.timestamp >= _since(minutes))
        .group_by("time")
        .order_by("time")
        .all()
    )
    return {"status": "success", "data": [{"time": row.time, "packets": row.packets} for row in rows]}

@router.get("/api/stats/protocols")
def get_protocols(db: Session = Depends(get_db)):
    total = db.query(func.count(LogTraffic.id)).scalar() or 0
    rows = (
        db.query(LogTraffic.protocol.label("label"), func.count(LogTraffic.id).label("count"))
        .filter(LogTraffic.timestamp >= _since(60))
        .group_by(LogTraffic.protocol)
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
        db.query(LogTraffic.port_target.label("port"), func.count(LogTraffic.id).label("count"))
        .filter(LogTraffic.timestamp >= _since(60))
        .group_by(LogTraffic.port_target)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    return {"status": "success", "data": [{"label": str(row.port or "Unknown"), "value": row.count} for row in rows]}

@router.get("/api/stats/top-sources")
def get_top_sources(limit: int = Query(5, ge=1, le=100), db: Session = Depends(get_db)):
    rows = (
        db.query(LogTraffic.ip_source.label("ip"), func.count(LogTraffic.id).label("packets"))
        .group_by(LogTraffic.ip_source)
        .order_by(desc("packets"))
        .limit(limit)
        .all()
    )
    blocked = {
        ip for (ip,) in db.query(BlacklistIP.ip_address).filter(BlacklistIP.status_active == True).all()
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