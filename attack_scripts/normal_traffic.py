"""
normal_traffic.py
------------------
Kịch bản giả lập LƯU LƯỢNG MẠNG BÌNH THƯỜNG (không phải tấn công): gửi mail
hợp lệ qua SMTP và kiểm tra hộp thư qua POP3 theo chu kỳ giãn cách tự nhiên
(có jitter ngẫu nhiên, không dồn dập). Dùng để tạo dữ liệu mẫu "normal"
giúp Tiên và Giàu kiểm thử luồng bắt gói tin (nids_engine/sniffer.py) và
ghi log, đối chứng với traffic bất thường từ các script khác trong
attack_scripts/ (ví dụ smtp_test.py — gửi dồn dập để giả lập spam/flood).

Khác với smtp_test.py (bắn EMAIL_COUNT email liên tục, DELAY nhỏ để tạo mật
độ cao), script này gửi RẤT ÍT, cách nhau nhiều giây/phút, xen kẽ với việc
đăng nhập POP3 kiểm tra mail — giống hành vi của một người dùng mail server
thật trong ngày làm việc.

Yêu cầu: một mail server test cục bộ đã cấu hình sẵn SMTP (cổng 25) và POP3
(cổng 110), ví dụ hMailServer trên 127.0.0.1, với tài khoản gửi/nhận hợp lệ.
"""

import argparse
import poplib
import random
import smtplib
import sys
import time
from datetime import datetime
from email.mime.text import MIMEText

# ==========================================
# CẤU HÌNH THÔNG SỐ KẾT NỐI HMAILSERVER
# ==========================================
TARGET_IP = "127.0.0.1"        # Địa chỉ IP của Mail Server (hoặc IP VPN khi test qua mạng ảo)
SMTP_PORT = 25                 # Cổng SMTP mặc định
POP3_PORT = 110                # Cổng POP3 mặc định
SENDER = "client@pbl4.local"       # Tài khoản gửi đã cấu hình trên hMailServer
RECEIVER = "admin@pbl4.local"      # Tài khoản nhận
POP3_USER = "admin@pbl4.local"     # Tài khoản dùng để đăng nhập kiểm tra hộp thư
POP3_PASSWORD = "changeme"         # Mật khẩu tài khoản POP3 (đổi theo cấu hình thật)

# Chu kỳ giãn cách: mỗi "vòng" gồm 1 lần gửi mail + 1 lần kiểm tra hộp thư,
# sau đó nghỉ một khoảng thời gian ngẫu nhiên trong [MIN_INTERVAL, MAX_INTERVAL]
# giây trước khi lặp lại — mô phỏng người dùng thật, không tạo mật độ cao.
MIN_INTERVAL = 20   # giây
MAX_INTERVAL = 60   # giây


def log(msg):
    stamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{stamp}] {msg}")
    sys.stdout.flush()


def send_normal_email(seq):
    """Gửi một email hợp lệ, đơn lẻ qua SMTP (hành vi người dùng bình thường)."""
    msg = MIMEText(f"Đây là email kiểm thử lưu lượng bình thường #{seq} từ PBL4 normal_traffic.py.")
    msg["Subject"] = f"PBL4 Normal Traffic #{seq}"
    msg["From"] = SENDER
    msg["To"] = RECEIVER

    try:
        with smtplib.SMTP(TARGET_IP, SMTP_PORT, timeout=5) as server:
            server.sendmail(SENDER, [RECEIVER], msg.as_string())
        log(f"[SMTP] Gửi thành công email #{seq} ({SENDER} -> {RECEIVER}).")
        return True
    except Exception as exc:
        log(f"[SMTP] Lỗi khi gửi email #{seq}: {exc}")
        return False


def check_mailbox():
    """Đăng nhập POP3, đếm số mail trong hộp thư rồi đăng xuất ngay (không xoá)."""
    try:
        conn = poplib.POP3(TARGET_IP, POP3_PORT, timeout=5)
        try:
            conn.user(POP3_USER)
            conn.pass_(POP3_PASSWORD)
            count, total_size = conn.stat()
            log(f"[POP3] Đăng nhập thành công ({POP3_USER}) - {count} mail, {total_size} byte.")
        finally:
            conn.quit()
        return True
    except Exception as exc:
        log(f"[POP3] Lỗi khi kiểm tra hộp thư: {exc}")
        return False


def run(rounds):
    log(f"Bắt đầu giả lập lưu lượng BÌNH THƯỜNG tới {TARGET_IP} "
        f"(SMTP:{SMTP_PORT}, POP3:{POP3_PORT}).")
    log(f"Số vòng: {'vô hạn' if rounds <= 0 else rounds} | "
        f"Giãn cách mỗi vòng: {MIN_INTERVAL}-{MAX_INTERVAL}s (ngẫu nhiên).")

    seq = 0
    try:
        while rounds <= 0 or seq < rounds:
            seq += 1
            log(f"--- Vòng {seq} ---")
            send_normal_email(seq)

            # Khoảng nghỉ nhỏ, ngẫu nhiên giữa gửi mail và kiểm tra hộp thư,
            # giống nhịp thao tác của người dùng thật hơn là gọi liên tiếp.
            time.sleep(random.uniform(1.5, 4.0))
            check_mailbox()

            wait_s = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
            log(f"Nghỉ {wait_s:.1f}s trước vòng tiếp theo...\n")
            time.sleep(wait_s)
    except KeyboardInterrupt:
        log("Đã dừng theo yêu cầu người dùng (Ctrl+C).")

    log("Kết thúc giả lập lưu lượng bình thường.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Giả lập lưu lượng mail bình thường (SMTP + POP3) cho PBL4 NIDS."
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=0,
        help="Số vòng gửi mail + kiểm tra hộp thư. 0 = chạy vô hạn tới khi Ctrl+C (mặc định).",
    )
    args = parser.parse_args()
    run(args.rounds)
