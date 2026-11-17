"""Chuyển dòng DB -> dict JSON thống nhất (dùng chung cho REST và WebSocket)."""


def iso(dt):
    """datetime (giờ local của máy chủ, không tz) -> ISO có offset, để trình duyệt ở múi giờ nào cũng hiển thị đúng."""
    return dt.astimezone().isoformat(timespec="seconds") if dt else None


def alert_to_dict(a) -> dict:
    return {
        "id": a.id,
        "source_ip": a.ip_source,
        "attack_type": a.attack_type,
        "severity": a.severity,
        "threshold_value": a.threshold_value,
        "created_at": iso(a.detected_at),
    }


def log_to_dict(l) -> dict:
    return {
        "id": l.id,
        "timestamp": iso(l.timestamp),
        "ip_source": l.ip_source,
        "protocol": l.protocol,
        "packet_count": l.packet_count,
        "port_target": l.port_target,
    }


def blocked_to_dict(b) -> dict:
    return {
        "id": b.id,
        "ip_address": b.ip_address,
        "reason": b.reason_blocked,
        "blocked_at": iso(b.created_at),
        "status": "Blocked" if b.status_active else "Unblocked",
    }
