"""
spam_mail.py
------------
Kịch bản giả lập tấn công Spam Mail / L7 Flood THỰC SỰ kết nối mạng (khác
với bản mock cũ chỉ in log giả rồi ghi thẳng vào MySQL). Script này dùng
smtplib để bắn một lượng lớn email liên tục tới hMailServer cục bộ trong
vòng vài giây, nhằm sinh ra lưu lượng SMTP thật cho nids_engine/sniffer.py
của Tiên bắt gói và tự phát hiện (rate-limit theo email/phút) — script
KHÔNG tự ghi cảnh báo vào DB, việc đó là trách nhiệm của NIDS Engine.

Khác với smtp_test.py (sinh traffic SMTP bình thường, tốc độ vừa phải) và
normal_traffic.py (mô phỏng người dùng thật), script này cố tình dồn dập
nhiều email trong thời gian ngắn để vượt ngưỡng Spam/Rate-limit.

Yêu cầu môi trường: hMailServer (hoặc server SMTP tương đương) đang chạy
trên TARGET_IP với tài khoản SENDER/RECEIVER tồn tại thật.

Cách chạy:
    python spam_mail.py
    python spam_mail.py --count 100 --delay 0.02
    python spam_mail.py --host 127.0.0.1 --port 25 --receiver admin@pbl4.local
"""

import argparse
import smtplib
import sys
import time
from datetime import datetime
from email.mime.text import MIMEText

# ==========================================
# CẤU HÌNH MẶC ĐỊNH (giống smtp_test.py / normal_traffic.py)
# ==========================================
TARGET_IP = "127.0.0.1"        # Mail server test cục bộ (hMailServer)
SMTP_PORT = 25
SENDER = "client@pbl4.local"
RECEIVER = "admin@pbl4.local"

SPAM_SUBJECTS = [
    "BAN DA TRUNG THUONG 1.000.000.000 VND!!!",
    "Click ngay de nhan qua tang mien phi",
    "Canh bao: Tai khoan cua ban sap bi khoa",
    "Giam gia 90% - Chi hom nay!!!",
    "Ban co 1 khoan tien dang cho duyet",
]

CONNECT_TIMEOUT = 4  # giây


def build_spam_message(index, sender, receiver):
    subject = SPAM_SUBJECTS[index % len(SPAM_SUBJECTS)]
    body = (
        f"Day la noi dung thu rac giả lập #{index} dùng để kiểm thử quy tắc "
        f"phát hiện Spam / Rate-limit của NIDS Engine (PBL4 Zero-Trust)."
    )
    msg = MIMEText(body)
    msg["Subject"] = f"[SPAM-TEST #{index}] {subject}"
    msg["From"] = sender
    msg["To"] = receiver
    return msg


def send_spam_burst(host, port, sender, receiver, count, delay):
    print("==============================================")
    print("   SPAM MAIL THẬT: SMTP BURST FLOOD           ")
    print("==============================================")
    print(f"[*] Mục tiêu: {host}:{port} | {sender} -> {receiver}")
    print(f"[*] Số lượng email: {count} | Độ trễ giữa các lần gửi: {delay}s")
    rate_per_min = 60 / delay if delay > 0 else float("inf")
    print(f"[*] Tốc độ ước tính: ~{rate_per_min:.0f} email/phút "
          f"(ngưỡng Spam/Rate-limit mặc định trong Config.jsx thường là 50/phút)\n")

    sent = 0
    start = time.time()

    for i in range(1, count + 1):
        stamp = datetime.now().strftime("%H:%M:%S")
        msg = build_spam_message(i, sender, receiver)
        try:
            server = smtplib.SMTP(host, port, timeout=CONNECT_TIMEOUT)
            server.sendmail(sender, [receiver], msg.as_string())
            server.quit()
            sent += 1
            sys.stdout.write(f"\r[{stamp}] Đã gửi {sent}/{count} email spam...")
            sys.stdout.flush()
            time.sleep(delay)
        except ConnectionRefusedError:
            print(f"\n\n[!!!] KẾT NỐI BỊ TỪ CHỐI TẠI EMAIL SỐ {i}.")
            print("[✓] Có thể NIDS đã phát hiện spam burst và Firewall đã chặn IP này.")
            break
        except smtplib.SMTPException as e:
            print(f"\n[!] Lỗi SMTP tại email {i}: {e}")
            break
        except OSError as e:
            print(f"\n\n[!!!] LỖI KẾT NỐI TẠI EMAIL SỐ {i}: {e}")
            print("[✓] Có thể Firewall/Zero-Trust đã drop traffic từ IP này.")
            break

    elapsed = time.time() - start
    print(f"\n\n[*] Kết thúc kịch bản spam mail.")
    print(f"[*] Đã gửi thành công {sent}/{count} email trong {elapsed:.1f}s "
          f"(~{(sent / elapsed * 60) if elapsed > 0 else 0:.0f} email/phút thực tế).")
    print("[*] Kiểm tra Dashboard (AlertsTable) / bảng blocked_ips để xác nhận NIDS đã phát hiện.")


def parse_args():
    parser = argparse.ArgumentParser(description="Giả lập tấn công Spam Mail / L7 Flood qua SMTP (kết nối mạng thật).")
    parser.add_argument("--host", default=TARGET_IP, help="IP mail server mục tiêu (mặc định 127.0.0.1)")
    parser.add_argument("--port", type=int, default=SMTP_PORT, help="Cổng SMTP (mặc định 25)")
    parser.add_argument("--sender", default=SENDER, help="Tài khoản gửi")
    parser.add_argument("--receiver", default=RECEIVER, help="Tài khoản nhận")
    parser.add_argument("--count", type=int, default=60, help="Số lượng email spam cần gửi")
    parser.add_argument("--delay", type=float, default=0.05,
                         help="Độ trễ (giây) giữa các lần gửi; mặc định 0.05s => ~1200 email/phút")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        send_spam_burst(args.host, args.port, args.sender, args.receiver, args.count, args.delay)
    except KeyboardInterrupt:
        sys.exit("\n[!] Đã dừng thủ công (Ctrl+C).")