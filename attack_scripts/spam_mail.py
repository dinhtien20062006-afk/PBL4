"""
spam_mail.py
------------
Kịch bản giả lập (mock) cảnh báo và log tấn công Spam Mail / L7 Flood
cho hệ thống PBL4 NIDS Zero-Trust (dựa trên cấu trúc mock_all_attacks.py).
"""

import pymysql
import time
import random
import sys
from datetime import datetime

# Cấu hình mục tiêu giả lập (hMailServer cục bộ)
TARGET_IP = "127.0.0.1"
SMTP_PORT = 25
SENDER = "client@pbl4.local"
RECEIVER = "admin@pbl4.local"
ATTACK_NAME = "SMTP Spam / L7 Flood"
MOCK_EMAIL_BURST = 25


def get_db_connection():
    """Kết nối tới MySQL của XAMPP (cùng cấu hình với mock_all_attacks.py)."""
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='pbl4_nids'
    )


def simulate_spam_mail():
    hacker_ip = f"{random.randint(11, 200)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    print("==============================================")
    print("   GIẢ LẬP KỊCH BẢN: SPAM MAIL (RATE LIMIT)   ")
    print("==============================================")
    print(f"[*] Mục tiêu giả định: {TARGET_IP}:{SMTP_PORT} ({SENDER} -> {RECEIVER})")
    print(f"[*] IP nguồn giả lập: {hacker_ip}\n")

    # Mô phỏng mật độ gửi email cao vượt ngưỡng Rate Limit
    for i in range(1, MOCK_EMAIL_BURST + 1):
        stamp = datetime.now().strftime("%H:%M:%S")
        sys.stdout.write(
            f"\r[{stamp}] [SMTP] Giả lập bản tin SMTP #{i}/{MOCK_EMAIL_BURST} "
            f"từ {hacker_ip} -> Tốc độ vượt ngưỡng cho phép..."
        )
        sys.stdout.flush()
        time.sleep(0.08)

    print("\n\n[*] NIDS đang phân tích mật độ gói tin SMTP...")
    time.sleep(1.0)
    print(f"[!] KÍCH HOẠT ZERO-TRUST: Thuật toán NIDS đã phát hiện hành vi {ATTACK_NAME}")
    print(f"[*] Kẻ tấn công đến từ IP: {hacker_ip}")
    print("[*] Đang ghi log cảnh báo vào Database và ra lệnh cho Firewall...")

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO blocked_ips (ip_address, attack_type) VALUES (%s, %s)"
            cursor.execute(sql, (hacker_ip, ATTACK_NAME))
        conn.commit()
        conn.close()
        print("[+] Thành công! Mở Web Dashboard để xem IP đã bị cập nhật lên bảng đen.")
    except Exception as e:
        print(f"[x] Lỗi khi kết nối MySQL XAMPP: {e}")


if __name__ == '__main__':
    simulate_spam_mail()