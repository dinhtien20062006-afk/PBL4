"""Cấu hình chung của Backend (đọc từ .env)."""
import os
import platform

from dotenv import load_dotenv

load_dotenv()


def _flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    return default if raw is None else raw.strip().lower() in {"1", "true", "yes", "on"}


# Chỉ thao tác Windows Firewall khi chạy trên Windows. Trên máy khác (dev Linux/Mac)
# backend chạy chế độ "chỉ ghi DB" để vẫn demo được giao diện.
FIREWALL_ENABLED = _flag("FIREWALL_ENABLED", platform.system() == "Windows")

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]

# Ngưỡng mặc định cho trang Cấu hình (có thể sửa trên giao diện, lưu ở bảng system_config).
DEFAULT_THRESHOLDS = {
    "spam_per_minute": 50,
    "brute_force_attempts": 5,
    "syn_packets_per_second": 50,
    "block_duration_seconds": 900,
}

# Tham số mặc định cho Attack Lab (trang /attack-lab, nút Bắt đầu gọi API thay vì chạy file tay).
# Có thể đổi trong backend/.env mà không cần sửa code.
ATTACK_TARGET_IP = os.getenv("ATTACK_TARGET_IP", "192.168.64.121")
ATTACK_VALID_EMAIL = os.getenv("ATTACK_VALID_EMAIL", "user01@company.local")
ATTACK_SMTP_PORT = int(os.getenv("ATTACK_SMTP_PORT", "25"))
ATTACK_POP3_PORT = int(os.getenv("ATTACK_POP3_PORT", "110"))
ATTACK_SYN_PORTS = [
    int(p) for p in os.getenv("ATTACK_SYN_PORTS", "25,110").split(",") if p.strip()
]
