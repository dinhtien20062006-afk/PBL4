import smtplib
import socket
import threading
import time
import random
from typing import Dict

# Biến lưu trạng thái phiên giả lập Spam Mail để Backend/Frontend theo dõi
spam_state: Dict = {
    "is_running": False,
    "target_ip": "",
    "valid_emails_sent": 0,
    "invalid_emails_sent": 0,
    "total_attempts": 0,
    "status_message": "Sẵn sàng",
    "blocked_by_firewall": False
}

_stop_event = threading.Event()


def _smtp_spam_worker(server_ip: str, port: int, valid_email: str, delay: float):
    """Luồng chạy ngầm bắn xen kẽ thư rác tới email thật và email ảo (không giới hạn số lần)"""
    global spam_state
    spam_state.update({
        "is_running": True,
        "target_ip": server_ip,
        "valid_emails_sent": 0,
        "invalid_emails_sent": 0,
        "total_attempts": 0,
        "status_message": f"Đang kích hoạt Spam Mail / DHA tới {server_ip}:{port}...",
        "blocked_by_firewall": False
    })

    count = 0
    # Vòng lặp vô hạn cho đến khi bấm Dừng hoặc bị Windows Firewall của Tiên chặn
    while not _stop_event.is_set():
        count += 1
        spam_state["total_attempts"] = count

        # Xen kẽ 2 kịch bản: Lượt lẻ bắn vào email thật, lượt chẵn bắn vào email rác không tồn tại
        is_valid_target = (count % 2 == 1)
        if is_valid_target:
            receiver = valid_email
        else:
            random_id = random.randint(1000, 99999)
            receiver = f"fake_user_{random_id}_{count}@company.local"

        sender = f"spammer_{random.randint(1, 500)}@evil.com"
        subject = f"Spam Mail Test #{count}"
        message = (
            f"From: {sender}\r\n"
            f"To: {receiver}\r\n"
            f"Subject: {subject}\r\n\r\n"
            f"Noi dung thu rac tu kich ban kiem thu Hybrid NIDS (Luot {count})."
        )

        try:
            # Kết nối tới dịch vụ SMTP của hMailServer (Tiên)
            server = smtplib.SMTP(server_ip, port, timeout=1.5)
            server.sendmail(sender, receiver, message)
            server.quit()

            # Nếu gửi tới email có thật thành công
            spam_state["valid_emails_sent"] += 1
            msg = f"Lượt {count}: Đã bắn mail rác tới tài khoản thật ({receiver})"
            print(f"[+] {msg}")
            spam_state["status_message"] = msg

        except smtplib.SMTPRecipientsRefused:
            # Server của Tiên từ chối nhận địa chỉ rác -> Sinh mã lỗi 550 User unknown trong Log!
            spam_state["invalid_emails_sent"] += 1
            msg = f"Lượt {count}: Bắn tới {receiver} -> Server trả về lỗi 550 User unknown"
            print(f"[!] {msg}")
            spam_state["status_message"] = msg

        except socket.timeout:
            # Gói tin bị thả (Drop) giữa chừng -> Windows Defender Firewall của Tiên đã khóa IP!
            msg = f"THÀNH CÔNG! Kết nối SMTP bị Firewall chặn (Timeout) tại lượt thứ {count}."
            print(f"[✔] {msg}")
            spam_state["blocked_by_firewall"] = True
            spam_state["status_message"] = msg
            break

        except ConnectionRefusedError:
            msg = f"LỖI KẾT NỐI: Cổng {port} trên {server_ip} đang đóng hoặc bị từ chối."
            print(f"[✘] {msg}")
            spam_state["status_message"] = msg
            break

        except Exception as e:
            msg = f"Kết nối bị ngắt đột ngột tại lượt {count}: {str(e)}"
            print(f"[-] {msg}")
            spam_state["status_message"] = msg
            break

        time.sleep(delay)

    if _stop_event.is_set() and not spam_state["blocked_by_firewall"]:
        spam_state["status_message"] = f"Đã dừng giả lập Spam Mail theo lệnh Admin (Tổng: {count} lượt)."

    spam_state["is_running"] = False


def start_smtp_spam_simulation(
    server_ip: str = "10.20.1.12",
    port: int = 25,
    valid_email: str = "user01@company.local",
    delay: float = 0.25
) -> Dict:
    """Hàm để Backend FastAPI gọi khi Frontend bấm nút Bắt đầu Spam"""
    if spam_state["is_running"]:
        return {"status": "warning", "message": "Kịch bản Spam Mail đang chạy rồi!"}

    _stop_event.clear()
    thread = threading.Thread(
        target=_smtp_spam_worker,
        args=(server_ip, port, valid_email, delay),
        daemon=True
    )
    thread.start()
    return {
        "status": "started",
        "message": f"Đã kích hoạt Spam Mail (Gửi tới {valid_email} & Email ảo) vào {server_ip}:{port}"
    }


def stop_smtp_spam_simulation() -> Dict:
    """Hàm để Backend FastAPI gọi khi Frontend bấm nút Dừng"""
    if not spam_state["is_running"]:
        return {"status": "idle", "message": "Không có tiến trình Spam Mail nào đang chạy."}
    _stop_event.set()
    return {"status": "stopping", "message": "Đang gửi tín hiệu dừng Spam Mail..."}


def get_smtp_spam_status() -> Dict:
    """Trả về thống kê số mail thật / mail ảo đã gửi cho Frontend"""
    return spam_state


# Vẫn hỗ trợ chạy độc lập trực tiếp từ Terminal nếu cần
if __name__ == "__main__":
    print("[!] Chạy độc lập script Spam Mail (Nhấn Ctrl+C để dừng)...")
    try:
        _smtp_spam_worker("10.20.1.12", 25, "user01@company.local", delay=0.25)
    except KeyboardInterrupt:
        _stop_event.set()
        print("\n[*] Đã dừng thủ công.")
