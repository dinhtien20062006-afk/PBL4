from fastapi import APIRouter

router = APIRouter(prefix="/api/blocked-ips", tags=["Blocked IPs"])

@router.get("/")
def get_blocked_ips_mockup():
    """Mockup API trả về danh sách IP bị chặn mẫu cho Frontend"""
    return {
        "status": "success",
        "data": [
            {"id": 1, "ip_address": "192.168.1.100", "reason": "DDoS Attack", "blocked_at": "2026-11-02T14:00:00Z"},
            {"id": 2, "ip_address": "203.0.113.50", "reason": "Brute Force SSH", "blocked_at": "2026-11-02T14:15:00Z"}
        ]
    }