from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cho phép Frontend (Vite dev server) gọi API trong lúc phát triển.
# TODO: khi deploy, thu hẹp allow_origins lại thành domain thật của Dashboard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# TODO(NIDS/DB): Đây là dữ liệu mẫu lưu tạm trong RAM để Frontend có endpoint
# thật để gọi trong lúc chờ MySQL + NIDS Engine ghi log. Khi tích hợp MySQL,
# thay list này bằng truy vấn SELECT trên bảng "ips" (mysql-connector-python)
# và thay các thao tác list dưới đây bằng UPDATE/INSERT tương ứng. Cấu trúc
# JSON trả về giữ nguyên để không phải sửa lại Frontend.
# ---------------------------------------------------------------------------
_ips_db = [
    {"ip": "192.168.1.14", "status": "normal", "proto": "TCP", "packets": 1284, "lastSeen": "2 giây trước", "blocked": False},
    {"ip": "10.0.0.82", "status": "suspicious", "proto": "TCP", "packets": 9531, "lastSeen": "5 giây trước", "blocked": False},
    {"ip": "203.0.113.55", "status": "suspicious", "proto": "TCP", "packets": 22890, "lastSeen": "32 giây trước", "blocked": True},
]


@app.get("/")
def read_root():
    return {"status": "NIDS & Mail Server System Running", "mode": "Zero-Trust Active"}


@app.get("/api/ips")
def list_ips():
    """Toàn bộ IP đang được NIDS theo dõi (bình thường + nghi ngờ)."""
    return _ips_db


@app.get("/api/blocked-ips")
def list_blocked_ips():
    """Chỉ những IP đã bị Zero-Trust Enforcer chặn trên Windows Firewall."""
    return [row for row in _ips_db if row["blocked"]]


@app.post("/api/ips/{ip}/block")
def block_ip(ip: str):
    for row in _ips_db:
        if row["ip"] == ip:
            row["blocked"] = True
            # TODO(Zero-Trust Enforcer): gọi netsh advfirewall / PowerShell ở đây
            # để thêm rule chặn thật trên Windows Defender Firewall.
            return row
    raise HTTPException(status_code=404, detail="IP not found")


@app.post("/api/ips/{ip}/unblock")
def unblock_ip(ip: str):
    for row in _ips_db:
        if row["ip"] == ip:
            row["blocked"] = False
            # TODO(Zero-Trust Enforcer): gọi netsh advfirewall để gỡ rule tương ứng.
            return row
    raise HTTPException(status_code=404, detail="IP not found")