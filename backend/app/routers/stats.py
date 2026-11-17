from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.cache import ttl_cached
from app.database import SessionLocal, get_db
from app.models import AlertHistory, BlacklistIP, LogTraffic
from app.serializers import iso

router = APIRouter(prefix="/api", tags=["Dashboard Statistics"])

# Mỗi dòng logs_traffic là số gói của 1 IP trong 1 giây -> tổng gói = SUM(packet_count)
PACKETS = func.coalesce(func.sum(LogTraffic.packet_count), 0)
PORT_NAMES = {25: "SMTP", 110: "POP3", 143: "IMAP", 465: "SMTPS", 587: "Submission", 993: "IMAPS", 995: "POP3S"}


def _since(minutes: int) -> datetime:
    return datetime.now() - timedelta(minutes=minutes)


CACHE_SECONDS = 3


@ttl_cached(CACHE_SECONDS)
def _traffic_by_ip() -> list[tuple]:
    """Tổng gói + lần cuối thấy của từng IP (quét toàn bảng -> cache)."""
    with SessionLocal() as db:
        rows = (
            db.query(
                LogTraffic.ip_source,
                PACKETS,
                func.max(LogTraffic.timestamp),
                func.max(LogTraffic.protocol),
            )
            .group_by(LogTraffic.ip_source)
            .order_by(desc(func.max(LogTraffic.timestamp)))
            .limit(200)
            .all()
        )
        return [(ip, int(pk), seen, proto) for ip, pk, seen, proto in rows]


@ttl_cached(CACHE_SECONDS)
def _alerted_ips() -> set[str]:
    with SessionLocal() as db:
        return {ip for (ip,) in db.query(AlertHistory.ip_source).distinct()}


@ttl_cached(CACHE_SECONDS)
def _packet_totals() -> tuple[int, int, int]:
    """(tổng gói, gói trong 1 phút gần nhất, tổng số cảnh báo)"""
    with SessionLocal() as db:
        total = int(db.query(PACKETS).scalar())
        last_minute = int(db.query(PACKETS).filter(LogTraffic.timestamp >= _since(1)).scalar())
        alerts = db.query(func.count(AlertHistory.id)).scalar() or 0
        return total, last_minute, alerts


@ttl_cached(CACHE_SECONDS)
def _top_packets(limit: int) -> list[tuple]:
    with SessionLocal() as db:
        rows = (
            db.query(LogTraffic.ip_source, PACKETS.label("packets"))
            .group_by(LogTraffic.ip_source)
            .order_by(desc("packets"))
            .limit(limit)
            .all()
        )
        return [(ip, int(pk)) for ip, pk in rows]


def _blocked_set(db: Session) -> set[str]:
    return {ip for (ip,) in db.query(BlacklistIP.ip_address).filter(BlacklistIP.status_active.is_(True))}


@router.get("/ips")
def list_ips(db: Session = Depends(get_db)):
    blocked = _blocked_set(db)  # bảng nhỏ, đọc trực tiếp để chặn/bỏ chặn hiện ngay
    alerted = _alerted_ips()
    data = [
        {
            "ip": ip,
            "status": "suspicious" if ip in alerted or ip in blocked else "normal",
            "proto": proto,
            "packets": packets,
            "last_seen": iso(seen),
            "blocked": ip in blocked,
        }
        for ip, packets, seen, proto in _traffic_by_ip()
    ]
    seen_ips = {d["ip"] for d in data}
    for ip in sorted(blocked - seen_ips):  # IP bị chặn nhưng chưa có traffic vẫn phải hiện
        data.append({"ip": ip, "status": "suspicious", "proto": "—", "packets": 0, "last_seen": None, "blocked": True})
    return {"status": "success", "total": len(data), "data": data}


@router.get("/stats/overview")
def overview(db: Session = Depends(get_db)):
    total, last_minute, alerts_total = _packet_totals()
    return {
        "status": "success",
        "data": {
            "packets_per_second": round(last_minute / 60, 2),
            "packets_last_minute": last_minute,
            "total_packets": total,
            "alerts_total": alerts_total,
            "blocked_total": db.query(func.count(BlacklistIP.id)).filter(BlacklistIP.status_active.is_(True)).scalar() or 0,
        },
    }


@router.get("/stats/traffic")
def traffic(minutes: int = Query(30, ge=1, le=1440), db: Session = Depends(get_db)):
    bucket = func.date_format(LogTraffic.timestamp, "%H:%i")
    # Bỏ phút hiện tại: chưa đủ dữ liệu nên đường biểu đồ sẽ rơi dốc về 0 ở điểm cuối.
    this_minute = datetime.now().replace(second=0, microsecond=0)
    rows = (
        db.query(bucket.label("time"), PACKETS.label("packets"), func.min(LogTraffic.timestamp).label("ts"))
        .filter(LogTraffic.timestamp >= this_minute - timedelta(minutes=minutes), LogTraffic.timestamp < this_minute)
        .group_by(bucket)
        .order_by("ts")
        .all()
    )
    return {"status": "success", "data": [{"time": r.time, "packets": int(r.packets)} for r in rows]}


@router.get("/stats/protocols")
def protocols(minutes: int = Query(60, ge=1, le=1440), db: Session = Depends(get_db)):
    rows = (
        db.query(LogTraffic.protocol.label("label"), PACKETS.label("count"))
        .filter(LogTraffic.timestamp >= _since(minutes))
        .group_by(LogTraffic.protocol)
        .all()
    )
    total = sum(int(r.count) for r in rows)
    return {
        "status": "success",
        "data": [
            {"label": r.label or "Unknown", "value": round(int(r.count) * 100 / total, 1) if total else 0}
            for r in sorted(rows, key=lambda r: -int(r.count))
        ],
    }


@router.get("/stats/ports")
def ports(minutes: int = Query(60, ge=1, le=1440), db: Session = Depends(get_db)):
    rows = (
        db.query(LogTraffic.port_target.label("port"), PACKETS.label("count"))
        .filter(LogTraffic.timestamp >= _since(minutes))
        .group_by(LogTraffic.port_target)
        .order_by(desc("count"))
        .limit(8)
        .all()
    )
    return {
        "status": "success",
        "data": [
            {
                "label": f"{PORT_NAMES[r.port]} · {r.port}" if r.port in PORT_NAMES else f"Cổng {r.port}",
                "value": int(r.count),
            }
            for r in rows
        ],
    }


@router.get("/stats/top-sources")
def top_sources(limit: int = Query(5, ge=1, le=100), db: Session = Depends(get_db)):
    blocked = _blocked_set(db)
    alerted = _alerted_ips()
    return {
        "status": "success",
        "data": [
            {
                "ip": ip,
                "packets": packets,
                "blocked": ip in blocked,
                "status": "suspicious" if ip in alerted or ip in blocked else "normal",
            }
            for ip, packets in _top_packets(limit)
        ],
    }
