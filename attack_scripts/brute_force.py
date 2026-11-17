import poplib
import socket
import threading
import time
from typing import Dict

# Biến lưu trạng thái phiên giả lập để Backend/Frontend theo dõi
simulation_state: Dict = {
    "is_running": False,
    "target_ip": "",
    "target_email": "",
    "attempts_sent": 0,
    "status_message": "Sẵn sàng",
    "blocked_by_firewall": False
}

_stop_event = threading.Event()


def _brute_force_worker(server_ip: str, port: int, target_email: str, max_attempts: int, delay: float):
    """Luồng chạy ngầm gửi mật khẩu sai liên tục tới cổng POP3 (110)"""
    global simulation_state
    simulation_state.update({
        "is_running": True,
        "target_ip": server_ip,
        "target_email": target_email,
        "attempts_sent": 0,
        "status_message": f"Đang tấn công Brute-force vào {server_ip}:{port}...",
        "blocked_by_firewall": False
    })

    for count in range(1, max_attempts + 1):
        if _stop_event.is_set():
            simulation_state["status_message"] = "Đã dừng giả lập theo lệnh của Admin."
            break

        simulation_state["attempts_sent"] = count
        try:
            # Kết nối tới hMailServer của Tiên với timeout 1.5s
            client = poplib.POP3(server_ip, port, timeout=1.5)
            client.user(target_email)
            client.pass_(f"wrong_pass_{count}")
            client.quit()

        except poplib.error_proto as e:
            # hMailServer từ chối đăng nhập -> Ghi log thành công
            msg = f"Lượt {count}/{max_attempts}: Đã bắn kết nối lỗi -> {e}"
            print(f"[+] {msg}")
            simulation_state["status_message"] = msg

        except (socket.timeout, ConnectionRefusedError, OSError):
            # Kết nối bị ngắt đột ngột -> Windows Firewall của Tiên đã chặn IP!
            msg = f"THÀNH CÔNG! Kết nối bị chặn tại lượt thứ {count} (Windows Firewall đã khóa IP)."
            print(f"[✔] {msg}")
            simulation_state["blocked_by_firewall"] = True
            simulation_state["status_message"] = msg
            break

        except Exception as e:
            msg = f"Lỗi kết nối mạng: {str(e)}"
            print(f"[-] {msg}")
            simulation_state["status_message"] = msg
            break

        time.sleep(delay)
    else:
        if not simulation_state["blocked_by_firewall"]:
            simulation_state["status_message"] = f"Hoàn tất {max_attempts} lượt gửi."

    simulation_state["is_running"] = False


def start_brute_force_simulation(
    server_ip: str = "192.168.64.121",
    port: int = 110,
    target_email: str = "user01@company.local",
    max_attempts: int = 150,
    delay: float = 0.2
) -> Dict:
    """Hàm để Backend FastAPI gọi khi Frontend bấm nút Bắt đầu"""
    if simulation_state["is_running"]:
        return {"status": "warning", "message": "Kịch bản Brute-force đang chạy, vui lòng đợi!"}

    _stop_event.clear()
    thread = threading.Thread(
        target=_brute_force_worker,
        args=(server_ip, port, target_email, max_attempts, delay),
        daemon=True
    )
    thread.start()
    return {"status": "started", "message": f"Đã kích hoạt giả lập Brute-force tới {server_ip}:{port}"}


def stop_brute_force_simulation() -> Dict:
    """Hàm để Backend FastAPI gọi khi Frontend bấm nút Dừng"""
    if not simulation_state["is_running"]:
        return {"status": "idle", "message": "Không có tiến trình nào đang chạy."}
    _stop_event.set()
    return {"status": "stopping", "message": "Đang gửi tín hiệu dừng tấn công..."}


def get_simulation_status() -> Dict:
    """Hàm trả về tiến trình hiện tại cho Frontend"""
    return simulation_state


# Vẫn hỗ trợ chạy độc lập trực tiếp từ Terminal nếu cần
if __name__ == "__main__":
    print("[!] Chạy độc lập script Brute-force...")
    _brute_force_worker("192.168.64.121", 110, "user01@company.local", max_attempts=300, delay=0.2)
