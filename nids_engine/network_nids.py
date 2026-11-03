from scapy.all import sniff, TCP, IP
from collections import Counter
import threading
import time
import requests

# Địa chỉ URL Endpoint API tiếp nhận lưu lượng mạng của Giàu
# (Cần thay thế '192.168.1.20' bằng IP thực tế trong mạng LAN của máy Giàu)
TRAFFIC_API_URL = "http://192.168.1.20:8000/api/logs/traffic"

# 1. Bộ đếm lưu lượng tổng quát (Toàn bộ gói tin TCP đi qua cổng 25, 110)
traffic_counter = Counter()

# 2. Bộ đếm gói tin SYN (Chỉ phục vụ riêng cho thuật toán phát hiện SYN Flood)
syn_counter = Counter()

def packet_callback(packet):
    """Hàm callback xử lý cho mỗi gói tin bắt được"""
    if packet.haslayer(TCP) and packet.haslayer(IP):
        ip_src = packet[IP].src
        dport = packet[TCP].dport
        tcp_flags = int(packet[TCP].flags)
        
        # Chỉ xử lý các gói tin hướng tới cổng dịch vụ Mail (25 hoặc 110)
        if dport in [25, 110]:
            # --- PHẦN 1: Thống kê lưu lượng chung (Tổng gói tin qua cổng 25, 110) ---
            traffic_counter[ip_src] += 1
            
            # --- PHẦN 2: Tần suất gói tin chứa cờ SYN (Phục vụ thuật toán SYN Flood) ---
            # Cờ SYN có giá trị bitwise là 2 (0x02)
            if tcp_flags & 0x02:
                syn_counter[ip_src] += 1
                print(f"[SYN DETECT] Phát hiện gói SYN từ IP: {ip_src} -> Port {dport} (Dùng cho thuật toán)")
            
            # Debug log gói tin tổng quát qua cổng mail
            print(f"[DEBUG] TCP Packet | {ip_src} -> Port {dport} | Flags: {tcp_flags}")

def reset_counter_periodic():
    """Hàm chạy ngầm định kỳ mỗi 1 giây: Gửi lưu lượng tổng quát sang Backend và reset bộ đếm"""
    while True:
        time.sleep(1)
        
        # Xử lý đẩy lưu lượng tổng quát (Traffic) sang Backend của Giàu
        if traffic_counter:
            print("\n--- [TRAFFIC LOG] Thống kê tổng quát gói tin trên cổng 25, 110/giây ---")
            for ip, count in traffic_counter.items():
                print(f"[+] IP Nguồn: {ip} | Tổng số gói tin: {count} pkts/s (Cổng 25/110)")
                
                # Payload chuẩn theo thiết kế API của Backend (/api/logs/traffic)
                payload = {
                    "ip_source": ip,
                    "packet_count": count,
                    "port_target": 25  # Hoặc trích xuất linh hoạt dport nếu cần chi tiết hơn
                }
                try:
                    # Bắn HTTP POST đồng bộ sang Backend để lưu database phục vụ biểu đồ Real-time
                    response = requests.post(TRAFFIC_API_URL, json=payload, timeout=1)
                    if response.status_code in [200, 201]:
                        pass # Đẩy dữ liệu traffic thành công
                except Exception as e:
                    # Bỏ qua lỗi kết nối tạm thời để luồng bắt gói tin không bị gián đoạn
                    pass
            
            # Reset bộ đếm lưu lượng tổng sau mỗi chu kỳ 1 giây
            traffic_counter.clear()

        # Xử lý riêng cho bộ đếm SYN (Dành cho thuật toán phát hiện SYN Flood / Ngưỡng DDoS)
        if syn_counter:
            for ip, syn_count in syn_counter.items():
                # Tại đây bạn có thể thêm logic so sánh ngưỡng SYN Flood (Threshold Check)
                # Ví dụ: nếu syn_count > SYN_THRESHOLD -> Kích hoạt cảnh báo / Chặn tường lửa
                pass
            syn_counter.clear()

def start_network_sniff():
    """Khởi chạy luồng bắt gói tin mạng"""
    print("[*] Module Network-based NIDS đang lắng nghe trên cổng 25 & 110 (hMailServer)...")
    
    # Chạy luồng định kỳ giải phóng và gửi dữ liệu lưu lượng độc lập (daemon thread)
    t = threading.Thread(target=reset_counter_periodic, daemon=True)
    t.start()
    
    # Hàm sniff của Scapy (store=0 giúp giải phóng bộ nhớ RAM khi bắt lượng packet lớn)
    # Lọc bộ lọc BPF tối ưu ngay từ tầng driver
    sniff(filter="tcp dst port 25 or tcp dst port 110", prn=packet_callback, store=0)

if __name__ == "__main__":
    # Test độc lập module mạng (Yêu cầu chạy Terminal / VS Code bằng quyền Administrator)
    start_network_sniff()
