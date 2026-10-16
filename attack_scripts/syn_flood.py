"""
syn_flood.py
------------
Kịch bản giả lập (mock) cảnh báo và log tấn công TCP SYN Flood
cho hệ thống PBL4 NIDS Zero-Trust (dựa trên cấu trúc mock_all_attacks.py).
"""

import pymysql
import time
import random
import sys
from datetime import datetime

# Cấu hình mục tiêu giả lập
TARGET_IP = "127.0.0.1"
TARGET_PORT = 25
ATTACK_NAME = "TCP SYN Flood Attack"
MOCK_BATCHES = 10


def get_db_connection():
    """Kết nối tới MySQL của XAMPP (cùng cấu hình với mock_all_attacks.py)."""
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='pbl4_nids'
    )


def simulate_syn_flood():
    hacker_ip = f"{random.randint(11, 200)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    print("==============================================")
    print("   GIẢ LẬP KỊCH BẢN: TCP SYN FLOOD ATTACK     ")
    print("==============================================")
    print(f"[*] Mục tiêu giả định: {TARGET_IP}:{TARGET_PORT} (Cờ TCP: SYN)")
    print(f"[*] IP nguồn giả lập: {hacker_ip}\n")

    # Mô phỏng lưu lượng gói tin SYN half-open tăng đột biến
    total_packets = 0
    for batch in range(1, MOCK_BATCHES + 1):
        stamp = datetime.now().strftime("%H:%M:%S")
        pkt_rate = random.randint(150, 350)
        total_packets += pkt_rate
        sys.stdout.write(
            f"\r[{stamp}] [TCP-SYN] Phát hiện luồng gói tin half-open đợt #{batch}/{MOCK_BATCHES}: "
            f"~{total_packets} packets (src={hacker_ip})"
        )
        sys.stdout.flush()
        time.sleep(0.15)

    print("\n\n[*] NIDS đang phân tích tỷ lệ gói tin SYN/ACK...")
    time.sleep(1.0)
    print(f"[!] KÍCH HOẠT ZERO-TRUST: Thuật toán NIDS đã phát hiện hành vi {ATTACK_NAME}")
    print(f"[*] Kẻ tấn công đến từ IP: {hacker_ip} (Tổng cộng ~{total_packets} gói SYN giả lập)")
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
    simulate_syn_flood()