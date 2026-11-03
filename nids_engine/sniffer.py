"""
Bắt gói tin thật bằng Scapy và đẩy vào MySQL qua Backend (POST /api/logs/ingest).
Chạy (cần quyền Admin/root và Npcap trên Windows):
    python nids_engine/sniffer.py            # bắt liên tục
    python nids_engine/sniffer.py 200        # bắt 200 gói rồi dừng
"""
import sys
import time

from scapy.all import sniff, IP, TCP, UDP, ICMP

from worker import log_queue, log_queue_join  # noqa: E402


def packet_callback(packet):
    if not packet.haslayer(IP):
        return
    ip = packet[IP]
    if packet.haslayer(TCP):
        proto, port = "TCP", packet[TCP].dport
    elif packet.haslayer(UDP):
        proto, port = "UDP", packet[UDP].dport
    elif packet.haslayer(ICMP):
        proto, port = "ICMP", 0
    else:
        proto, port = str(ip.proto), 0
    data = {
        "source_ip": ip.src,
        "dest_ip": ip.dst,
        "port": port,
        "protocol": proto,
        "packet_size": len(packet),
        "status": "Normal",
    }
    try:
        log_queue.put_nowait(data)
    except Exception:
        print("Queue đầy, bỏ qua gói tin")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print("[*] Đang bắt gói tin... (Ctrl+C để dừng)")
    try:
        sniff(prn=packet_callback, store=False, count=count)
    except KeyboardInterrupt:
        pass
    log_queue_join()
    print("[*] Đã dừng.")
