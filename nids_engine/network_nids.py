from scapy.all import sniff, TCP, IP
from collections import Counter
import threading
import time
import requests

# Địa chỉ URL Endpoint API tiếp nhận lưu lượng và cảnh báo của Giàu
# (Cần thay thế '192.168.1.20' bằng IP thực tế trong mạng LAN của máy Giàu)
TRAFFIC_API_URL = "http://192.168.1.20:8000/api/logs/traffic"
ALERT_API_URL = "http://192.168.1.20:8000/api/alerts/trigger"

# Cấu hình ngưỡng phát hiện SYN Flood (Ví dụ: > 50 gói SYN trong 1 giây từ một IP)
SYN_THRESHOLD = 50

# Bộ đếm lưu lượng và bộ đếm SYN riêng biệt
traffic_counter = Counter()
syn_counter = Counter()

# Khóa luồng (Thread Lock) đảm bảo an toàn dữ liệu khi cập nhật/xóa Counter song song
counter_lock = threading.Lock()

def packet_callback(packet):
    """Hàm callback xử lý cho mỗi gói tin bắt được"""
    if packet.haslayer(TCP) and packet.haslayer(IP):
        ip_src = packet[IP].src
        dport = packet[TCP].dport
        tcp_flags = int(packet[TCP].flags)
        
        # Chỉ xử lý các gói tin hướng tới cổng dịch vụ Mail (25 hoặc 110)
        if dport in [25, 110]:
            with counter_lock:
                # --- PHẦN 1: Thống kê lưu lượng chung (Tổng gói tin qua cổng 25, 110) ---
                traffic_counter[ip_src] += 1
                
                # --- PHẦN 2: Tần suất gói tin chứa cờ SYN (Thuật toán SYN Flood) ---
                # Cờ SYN có giá trị bitwise là 2 (0x02)
                if tcp_flags & 0x02:
                    syn_counter[ip_src] += 1
            
            # Debug log (có thể comment lại nếu lượng packet quá lớn gây tràn terminal)
            # print(f"[DEBUG] TCP Packet | {ip_src} -> Port {dport} | Flags: {tcp_flags}")

def reset_counter_periodic():
    """Hàm chạy ngầm định kỳ mỗi 1 giây: Gửi lưu lượng, kiểm tra ngưỡng SYN Flood và reset bộ đếm"""
    while True:
        time.sleep(1)
        
        # Lấy snapshot dữ liệu an toàn bằng Lock sau đó reset bộ đếm ngay lập tức
        with counter_lock:
            current_traffic = traffic_counter.copy()
            current_syn = syn_counter.copy()
            traffic_counter.clear()
            syn_counter.clear()
        
        # 1. Đẩy lưu lượng tổng quát (Traffic) sang Backend của Giàu
        if current_traffic:
            for ip, count in current_traffic.items():
                payload = {
                    "ip_source": ip,
                    "packet_count": count,
                    "port_target": 25  # Hoặc trích xuất linh hoạt port nếu cần
                }
                try:
                    requests.post(TRAFFIC_API_URL, json=payload, timeout=0.5)
                except Exception:
                    pass
        
        # 2. Xử lý thuật toán phát hiện SYN Flood (Threshold Check)
        if current_syn:
            for ip, syn_count in current_syn.items():
                if syn_count > SYN_THRESHOLD:
                    print(f"\n[!] CẢNH BÁO SYN FLOOD: Phát hiện IP {ip} gửi {syn_count} gói SYN/s (Vượt ngưỡng {SYN_THRESHOLD})!")
                    
                    # Payload cảnh báo gửi sang Backend để lưu DB và đẩy WebSocket Real-time
                    alert_payload = {
                        "ip_source": ip,
                        "attack_type": "SYN Flood",
                        "threshold_value": syn_count
                    }
                    try:
                        response = requests.post(ALERT_API_URL, json=alert_payload, timeout=0.5)
                        if response.status_code in [200, 201]:
                            print(f"[+] Đã gửi cảnh báo SYN Flood của IP {ip} lên Backend thành công.")
                    except Exception as e:
                        print(f"[-] Lỗi kết nối API cảnh báo: {e}")
                    
                    # (Tùy chọn tự động hóa): Tại đây có thể gọi trực tiếp block_ip(ip) từ firewall_manager 
                    # để khóa ngay lập tức trên Windows Firewall ở tầng mạng.

def start_network_sniff():
    """Khởi chạy luồng bắt gói tin mạng NIDS"""
    print("[*] Module Network-based NIDS đang lắng nghe trên cổng 25 & 110 (hMailServer)...")
    
    # Khởi chạy luồng định kỳ giải phóng và gửi dữ liệu độc lập (daemon thread)
    t = threading.Thread(target=reset_counter_periodic, daemon=True)
    t.start()
    
    # Hàm sniff của Scapy (store=0 giúp giải phóng RAM khi bắt lượng packet lớn)
    # Lọc BPF tối ưu ngay từ tầng driver
    sniff(filter="tcp dst port 25 or tcp dst port 110", prn=packet_callback, store=0)

if __name__ == "__main__":
    # Test độc lập module mạng (Yêu cầu chạy Terminal / VS Code bằng quyền Administrator)[cite: 1, 2]
    start_network_sniff()
