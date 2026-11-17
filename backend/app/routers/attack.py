"""Attack Lab: cho phép Frontend bấm nút để chạy/dừng 3 kịch bản giả lập tấn công
(attack_scripts/syn_flood.py, smtp_spam.py, brute_force.py) thay vì phải mở Terminal
và chạy file thủ công. Mỗi script đã tự quản lý thread nền + biến trạng thái toàn cục
(is_running, packets_sent/attempts_sent, status_message, blocked_by_firewall) — router
này chỉ gọi các hàm start_*/stop_*/get_*_status() có sẵn của script.
"""
import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import (
    ATTACK_POP3_PORT,
    ATTACK_SMTP_PORT,
    ATTACK_SYN_PORTS,
    ATTACK_TARGET_IP,
    ATTACK_VALID_EMAIL,
)
from app.schemas import AttackStartRequest

logger = logging.getLogger(__name__)

# attack_scripts/ nằm ở thư mục gốc dự án (ngang hàng với backend/), không phải trong app/.
# Thêm thư mục gốc vào sys.path để import được dù uvicorn chạy từ trong backend/.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_IMPORT_ERROR = None
try:
    from attack_scripts import brute_force, smtp_spam, syn_flood
except Exception as exc:  # thiếu scapy, hoặc chạy sai cấu trúc thư mục
    syn_flood = smtp_spam = brute_force = None
    _IMPORT_ERROR = str(exc)
    logger.warning("Không import được attack_scripts: %s", exc)

router = APIRouter(prefix="/api/attack", tags=["Attack Lab"])

# id dùng trên URL <-> module tương ứng trong attack_scripts/
_SCRIPT_IDS = ("syn_flood", "smtp_spam", "brute_force")


def _module(script_id: str):
    if script_id not in _SCRIPT_IDS:
        raise HTTPException(404, f"Không có kịch bản '{script_id}'. Chọn một trong: {', '.join(_SCRIPT_IDS)}")
    mod = {"syn_flood": syn_flood, "smtp_spam": smtp_spam, "brute_force": brute_force}[script_id]
    if mod is None:
        raise HTTPException(
            503,
            f"Không nạp được attack_scripts (thiếu thư viện, ví dụ scapy?): {_IMPORT_ERROR}",
        )
    return mod


def _status_of(script_id: str, mod) -> dict:
    if script_id == "syn_flood":
        return mod.get_syn_flood_status()
    if script_id == "smtp_spam":
        return mod.get_smtp_spam_status()
    return mod.get_simulation_status()


@router.get("/status")
def all_status():
    """Trạng thái của cả 3 kịch bản trong 1 request — Frontend chỉ cần poll endpoint này."""
    if _IMPORT_ERROR:
        raise HTTPException(503, f"Không nạp được attack_scripts: {_IMPORT_ERROR}")
    return {sid: _status_of(sid, _module(sid)) for sid in _SCRIPT_IDS}


@router.get("/{script_id}/status")
def one_status(script_id: str):
    mod = _module(script_id)
    return _status_of(script_id, mod)


@router.post("/{script_id}/start")
def start(script_id: str, body: AttackStartRequest = AttackStartRequest()):
    mod = _module(script_id)
    target_ip = body.target_ip or ATTACK_TARGET_IP

    try:
        if script_id == "syn_flood":
            result = mod.start_syn_flood_simulation(
                target_ip=target_ip,
                target_ports=[body.port] if body.port else list(ATTACK_SYN_PORTS),
                packets_per_sec=body.packets_per_sec or 150,
            )
        elif script_id == "smtp_spam":
            result = mod.start_smtp_spam_simulation(
                server_ip=target_ip,
                port=body.port or ATTACK_SMTP_PORT,
                valid_email=body.valid_email or ATTACK_VALID_EMAIL,
                delay=body.delay if body.delay is not None else 0.25,
            )
        else:
            result = mod.start_brute_force_simulation(
                server_ip=target_ip,
                port=body.port or ATTACK_POP3_PORT,
                target_email=body.valid_email or ATTACK_VALID_EMAIL,
                max_attempts=body.max_attempts or 150,
                delay=body.delay if body.delay is not None else 0.2,
            )
    except Exception as exc:  # vd. thiếu quyền Admin (SYN Flood cần Npcap + raw socket)
        logger.exception("Lỗi khi khởi chạy kịch bản %s", script_id)
        raise HTTPException(500, f"Không thể khởi chạy kịch bản '{script_id}': {exc}") from exc

    return {**result, "script_id": script_id, "status_snapshot": _status_of(script_id, mod)}


@router.post("/{script_id}/stop")
def stop(script_id: str):
    mod = _module(script_id)
    if script_id == "syn_flood":
        result = mod.stop_syn_flood_simulation()
    elif script_id == "smtp_spam":
        result = mod.stop_smtp_spam_simulation()
    else:
        result = mod.stop_brute_force_simulation()
    return {**result, "script_id": script_id}
