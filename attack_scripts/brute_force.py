"""
brute_force.py
---------------
Kịch bản giả lập (mock) cảnh báo và log tấn công Brute Force POP3/SMTP
cho hệ thống PBL4 NIDS Zero-Trust (dựa trên cấu trúc mock_all_attacks.py).
"""

import pymysql
import time
import random
import sys
from datetime import datetime

# Cấu hình mục tiêu giả lập (hMailServer cục bộ)
TARGET_IP = "127.0.0.1"
POP3_PORT = 110
TARGET_USER = "admin@pbl4.local"
ATTACK_NAME = "Password Brute Force"
MAX_MOCK_ATTEMPTS = 10


def get_db_connection():
    """Kết nối tới MySQL của XAMPP (cùng cấu hình với mock_all_attacks.py)."""
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='pbl4_nids'
    )


def simulate_brute_force():
    hacker_ip = f"{random.randint(11, 200)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    print("==============================================")
    print("   GIẢ LẬP KỊCH BẢN: BRUTE FORCE POP3/SMTP    ")
    print("==============================================")
    print(f"[*] Mục tiêu giả định: {TARGET_IP}:{POP3_PORT} (Tài khoản: {TARGET_USER})")
    print(f"[*] IP nguồn giả lập: {hacker_ip}\n")

    # Mô phỏng quá trình thử mật khẩu thất bại trên console
    for attempt in range(1, MAX_MOCK_ATTEMPTS + 1):
        stamp = datetime.now().strftime("%H:%M:%S")
        fake_pass = f"pass_test_{random.randint(1000, 9999)}"
        sys.stdout.write(
            f"\r[{stamp}] [POP3] Lần thử #{attempt}/{MAX_MOCK_ATTEMPTS} "
            f"({TARGET_USER}:{fake_pass}) -> -ERR Authentication failed"
        )
        sys.stdout.flush()
        time.sleep(0.25)

    print("\n\n[*] NIDS đang phân tích chuỗi sự kiện đăng nhập thất bại...")
    time.sleep(1.0)
    print(f"[!] KÍCH HOẠT ZERO-TRUST: Thuật toán NIDS đã phát hiện hành vi {ATTACK_NAME}")
    print(f"[*] Kẻ tấn công đến từ IP: {hacker_ip} (Vượt ngưỡng {MAX_MOCK_ATTEMPTS} lần sai liên tiếp)")
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
    simulate_brute_force()