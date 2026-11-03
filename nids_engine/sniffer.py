"""Bắt gói tin thật bằng Scapy và đẩy vào MySQL (qua API /api/logs/ingest).

Chạy (cần quyền Admin/root; Windows cần cài Npcap):
    cd nids_engine
    python sniffer.py
"""
from scapy.all import sniff, IP, TCP, UDP, ICMP

from worker import log_queue
import queue


def packet_callback(packet):
    if not packet.haslayer(IP):
        return
    ip = packet[IP]
    port, proto = 0, "Khác"
    if packet.haslayer(TCP):
        proto, port = "TCP", packet[TCP].dport
    elif packet.haslayer(UDP):
        proto, port = "UDP", packet[UDP].dport
    elif packet.haslayer(ICMP):
        proto = "ICMP"
    try:
        log_queue.put_nowait({
            "source_ip": ip.src,
            "dest_ip": ip.dst,
            "port": port,
            "protocol": proto,
            "packet_size": len(packet),
            "status": "Normal",
        })
    except queue.Full:
        print("Cảnh báo: Queue đầy, hệ thống quá tải!")


if __name__ == "__main__":
    print("[*] Đang bắt gói tin... (Ctrl+C để dừng)")
    sniff(prn=packet_callback, store=False)
