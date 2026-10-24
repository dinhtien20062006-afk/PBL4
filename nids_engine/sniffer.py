from scapy.all import sniff, IP, TCP
import queue
import time

# Hàng đợi tạm thời (Queue) để lưu trữ thông tin gói tin trước khi đẩy về Backend
packet_queue = queue.Queue(maxsize=1000)

def packet_callback(packet):
    """
    Hàm xử lý mỗi khi Scapy bắt được một gói tin trên mạng.
    """
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
                    "flags": str(flags)
                }
                
                # Đẩy vào Queue để sẵn sàng cho luồng Backend xử lý
                if not packet_queue.full():
                    packet_queue.put(packet_info)
                
                print(f"[NIDS CAPTURED] {protocol} | {src_ip}:{src_port} -> {dst_ip}:{dst_port} | Flags: {flags} | Len: {payload_length}")

    except Exception as e:
        print(f"[ERROR] Lỗi khi bóc tách gói tin: {e}")

def start_sniffer(interface=None):
    """
    Khởi động tiến trình bắt gói tin liên tục.
    """
    print("[*] Bắt đầu khởi động NIDS Packet Sniffer Engine...")
    # Lọc chỉ bắt các gói tin TCP có liên quan đến port 25 hoặc 110 để tối ưu hiệu suất
    bpf_filter = "tcp port 25 or tcp port 110"
    
    # Chạy hàm sniff liên tục (store=0 giúp giải phóng RAM, tránh bị tràn bộ nhớ)
    sniff(filter=bpf_filter, prn=packet_callback, store=0, iface=interface)

if __name__ == "__main__":
    # Test thử nghiệm độc lập module sniffer
    print("=== ĐANG CHẠY KIỂM THỬ NIDS SNIFFER CORE ===")
    start_sniffer()