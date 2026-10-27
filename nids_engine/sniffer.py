from scapy.all import sniff, IP, TCP, conf
import argparse
import queue
import sys
import time
import threading

# Hàng đợi tạm thời (Queue) để lưu trữ thông tin gói tin trước khi đẩy về Backend
packet_queue = queue.Queue(maxsize=1000)

_last_packet_time = None
_captured_count = 0


def packet_callback(packet):
    """
    Hàm xử lý mỗi khi Scapy bắt được một gói tin trên mạng.
    """
    global _last_packet_time, _captured_count
    try:
        # Kiểm tra xem gói tin có chứa tầng IP và tầng TCP hay không
        if packet.haslayer(IP) and packet.haslayer(TCP):
            ip_layer = packet[IP]
            tcp_layer = packet[TCP]

            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            src_port = tcp_layer.sport
            dst_port = tcp_layer.dport

            # Lọc các gói tin thuộc cổng dịch vụ Mail: Port 25 (SMTP) và Port 110 (POP3)
            if src_port in [25, 110] or dst_port in [25, 110]:
                protocol = "SMTP" if (src_port == 25 or dst_port == 25) else "POP3"
                payload_length = len(packet[TCP].payload) if packet[TCP].payload else 0

                # Trích xuất các TCP Flags (SYN, ACK, FIN, PSH...)
                flags = tcp_layer.flags

                # Đóng gói thông tin thành một Dictionary tạm thời
                packet_info = {
                    "timestamp": time.time(),
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "src_port": src_port,
                    "dst_port": dst_port,
                    "protocol": protocol,
                    "payload_length": payload_length,
                    "flags": str(flags),
                }

                # Đẩy vào Queue để sẵn sàng cho luồng Backend xử lý
                if not packet_queue.full():
                    packet_queue.put(packet_info)

                _last_packet_time = time.time()
                _captured_count += 1
                print(
                    f"[NIDS CAPTURED] #{_captured_count} {protocol} | "
                    f"{src_ip}:{src_port} -> {dst_ip}:{dst_port} | "
                    f"Flags: {flags} | Len: {payload_length}",
                    flush=True,  # tránh bị Windows console buffer, tưởng như "đông cứng"
                )

    except Exception as e:
        print(f"[ERROR] Lỗi khi bóc tách gói tin: {e}", flush=True)


def _heartbeat():
    """In nhịp "còn sống" mỗi 10s để xác nhận sniffer không bị treo thật sự,
    vì rất khó phân biệt với trường hợp nó chỉ đang *không thấy gói tin nào*
    do chọn sai network interface (ví dụ không chọn Npcap Loopback Adapter
    khi test với 127.0.0.1)."""
    while True:
        time.sleep(10)
        if _last_packet_time is None:
            print(
                "[*] ... vẫn đang lắng nghe, CHƯA bắt được gói tin nào phù hợp. "
                "Nếu đang test với 127.0.0.1, kiểm tra đã chọn đúng "
                "'Npcap Loopback Adapter' chưa (xem --list-interfaces).",
                flush=True,
            )
        else:
            idle = time.time() - _last_packet_time
            print(f"[*] ... vẫn đang lắng nghe (gói gần nhất cách đây {idle:.0f}s).", flush=True)


def _list_cached_ifaces():
    """Lấy danh sách interface từ bộ nhớ đệm mà scapy đã dựng sẵn lúc import
    (KHÔNG gọi lại WMI/Get-NetAdapter lần nữa — đây là nguyên nhân hay gây
    treo/chậm nhiều giây-phút trên Windows có nhiều card ảo)."""
    out = []
    try:
        for iface in conf.ifaces.values():
            name = getattr(iface, "name", "") or ""
            desc = getattr(iface, "description", "") or name
            out.append((name, desc))
    except Exception as e:
        print(f"[!] Không đọc được danh sách interface từ cache: {e}", flush=True)
    return out


def list_interfaces():
    """Liệt kê các network interface mà scapy nhìn thấy trên máy."""
    ifaces = _list_cached_ifaces()
    print("=== DANH SÁCH NETWORK INTERFACE (scapy nhìn thấy) ===")
    for name, desc in ifaces:
        marker = "  <-- dùng cái này để bắt traffic 127.0.0.1" if "loopback" in desc.lower() else ""
        print(f"  - {desc}{marker}")
    print('\nChạy lại với: python sniffer.py --iface "<tên description ở trên>"')


def _auto_find_loopback_iface():
    """Tự động tìm Npcap Loopback Adapter nếu có, để bắt traffic 127.0.0.1."""
    for name, desc in _list_cached_ifaces():
        if "loopback" in desc.lower():
            return name or desc
    return None


def start_sniffer(interface=None, skip_auto=False):
    """
    Khởi động tiến trình bắt gói tin liên tục.
    """
    print("[*] Bắt đầu khởi động NIDS Packet Sniffer Engine...", flush=True)

    if interface is None and skip_auto:
        print("[*] Bỏ qua bước tự dò interface (--no-auto-iface) -> dùng mặc định của scapy.", flush=True)
    elif interface is None:
        print("[*] Đang dò Npcap Loopback Adapter trong cache interface của scapy...", flush=True)
        auto_iface = _auto_find_loopback_iface()
        if auto_iface:
            interface = auto_iface
            print(f"[*] Tự động chọn Npcap Loopback Adapter: {interface}", flush=True)
        else:
            print(
                "[!] Không tự tìm thấy Npcap Loopback Adapter. Đang dùng interface "
                "mặc định của scapy -> SẼ KHÔNG bắt được traffic tới 127.0.0.1. "
                "Chạy 'python sniffer.py --list-interfaces' để chọn thủ công qua --iface.",
                flush=True,
            )

    # Lọc chỉ bắt các gói tin TCP có liên quan đến port 25 hoặc 110 để tối ưu hiệu suất
    bpf_filter = "tcp port 25 or tcp port 110"

    threading.Thread(target=_heartbeat, daemon=True).start()

    print(f"[*] Đang lắng nghe (iface={interface or 'mặc định'}, filter='{bpf_filter}')...", flush=True)
    # Chạy hàm sniff liên tục (store=0 giúp giải phóng RAM, tránh bị tràn bộ nhớ)
    sniff(filter=bpf_filter, prn=packet_callback, store=0, iface=interface)


def parse_args():
    parser = argparse.ArgumentParser(description="NIDS Packet Sniffer (SMTP/POP3) cho PBL4.")
    parser.add_argument("--iface", default=None, help="Tên/description interface để bắt gói tin")
    parser.add_argument("--list-interfaces", action="store_true", help="Liệt kê interface rồi thoát")
    parser.add_argument("--no-auto-iface", action="store_true",
                         help="Bỏ qua bước tự dò Loopback Adapter, dùng interface mặc định của scapy")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.list_interfaces:
        list_interfaces()
        sys.exit(0)

    print("=== ĐANG CHẠY KIỂM THỬ NIDS SNIFFER CORE ===", flush=True)
    try:
        start_sniffer(interface=args.iface, skip_auto=args.no_auto_iface)
    except KeyboardInterrupt:
        sys.exit("\n[!] Đã dừng thủ công (Ctrl+C).")
    except Exception as e:
        sys.exit(
            f"\n[x] Lỗi khi khởi động sniffer: {e}\n"
            "    Kiểm tra: (1) đã chạy PowerShell quyền Administrator chưa, "
            "(2) đã cài Npcap chưa, (3) thử 'python sniffer.py --list-interfaces'."
        )
