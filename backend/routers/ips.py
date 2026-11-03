from collections import Counter, defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, BlockedIP, TrafficLog

router = APIRouter(prefix="/api/ips", tags=["IPs"])


@router.get("")
def list_monitored_ips(limit: int = 100, db: Session = Depends(get_db)):
    """Danh sách IP đang theo dõi, tổng hợp từ traffic_logs + alerts + blocked_ips."""
    agg = (
        db.query(
            TrafficLog.source_ip,
            func.count(TrafficLog.id),
            func.max(TrafficLog.timestamp),
        )
        .group_by(TrafficLog.source_ip)
        .order_by(func.count(TrafficLog.id).desc())
        .limit(limit)
        .all()
    )

    # Giao thức xuất hiện nhiều nhất của từng IP
    proto_rows = (
        db.query(TrafficLog.source_ip, TrafficLog.protocol, func.count(TrafficLog.id))
        .group_by(TrafficLog.source_ip, TrafficLog.protocol)
        .all()
    )
    protos = defaultdict(Counter)
    for ip, proto, n in proto_rows:
        protos[ip][proto or "—"] += n

    suspicious_from_logs = {
        r[0]
        for r in db.query(TrafficLog.source_ip)
        .filter(TrafficLog.status != "Normal")
        .distinct()
        .all()
    }
    alerted = {r[0] for r in db.query(Alert.source_ip).distinct().all()}
    blocked = {
        r[0] for r in db.query(BlockedIP.ip_address).filter(BlockedIP.status == "Blocked").all()
    }

    result, seen = [], set()
    for ip, packets, last_seen in agg:
        seen.add(ip)
        result.append(
            {
                "ip": ip,
                "packets": packets,
                "proto": protos[ip].most_common(1)[0][0] if protos[ip] else "—",
                "last_seen": last_seen.isoformat() if last_seen else None,
                "status": "suspicious" if ip in suspicious_from_logs or ip in alerted else "normal",
                "blocked": ip in blocked,
            }
        )

    # IP đang bị chặn nhưng chưa có traffic trong log vẫn phải hiện trong danh sách
    for ip in blocked - seen:
        result.append(
            {"ip": ip, "packets": 0, "proto": "—", "last_seen": None, "status": "suspicious", "blocked": True}
        )

    return {"status": "success", "total": len(result), "data": result}
