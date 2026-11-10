import time
import os
import re
import queue
import requests
import threading
from collections import defaultdict
from watchdog.observers.polling import PollingObserver as Observer  # Ổn định trên Windows
from watchdog.events import FileSystemEventHandler

# Import module tường lửa Zero-Trust đã viết ở Tuần 2 (Tiên)
from firewall_manager import block_ip

# ==================== CẤU HÌNH HỆ THỐNG ====================
# Địa chỉ IP và Endpoint Backend FastAPI của Giàu (Cần thay đổi IP thực tế trong mạng LAN)
BACKEND_URL = "http://192.168.1.20:8000/api/alerts/trigger"

# Cấu hình ngưỡng an toàn (Thresholds) theo đề tài[cite: 1]
AUTH_FAIL_THRESHOLD = 25   
SPAM_FAIL_THRESHOLD = 25   

# Bộ nhớ tạm theo dõi vi phạm theo cơ chế Sliding Window: { ip: [timestamp1, timestamp2, ...] }
auth_violations = defaultdict(list)
spam_violations = defaultdict(list)

# Hàng đợi bất đồng bộ (Async Queue) để gửi HTTP Request ngầm báo động sang Backend, tránh nghẽn luồng
request_queue = queue.Queue()

def background_request_worker():
    """Luồng ngầm liên tục xử lý các request gửi cảnh báo sang Backend của Giàu"""
    while True:
        url, payload = request_queue.get()
        try:
            response = requests.post(url, json=payload, timeout=3)
            if response.status_code in [200, 201]:
                print(f"[🔥 TRIGGER] Đã đẩy cảnh báo '{payload.get('attack_type')}' của IP {payload.get('ip_source')} sang Backend thành công!")
            else:
                print(f"[-] Backend trả về lỗi khi nhận alert: {response.status_code}")
        except Exception as e:
            print(f"[-] Không thể kết nối tới Backend của Giàu: {e}")
        finally:
            request_queue.task_done()

# Khởi chạy luồng worker ngầm
t_worker = threading.Thread(target=background_request_worker, daemon=True)
t_worker.start()

def clean_old_timestamps(violation_list):
    """Xóa các mốc thời gian quá 1 phút (60 giây) để tính tần suất theo cơ chế Sliding Window[cite: 1]"""
    now = time.time()
    return [t for t in violation_list if now - t <= 60]

def trigger_alert_and_block(ip_source, attack_type, total_faults):
    """Hàm thực thi Zero-Trust Tuần 5: Khóa IP trên Windows Firewall trước, đẩy báo động Backend sau"""
    print(f"\n[🛡️ ZERO-TRUST ENFORCER] Phát hiện tấn công từ IP: {ip_source} ({attack_type})!")
    print(f"[🛡️ ENFORCER] Đang tự động kích hoạt tường lửa cô lập IP tại Windows Defender Firewall...")
    
    # 1. Gọi module Firewall (Tuần 2) để khóa cứng IP tức thời tại tầng hệ điều hành
    firewall_success = block_ip(ip_source)
    if firewall_success:
        print(f"[+ SUCCESS] IP {ip_source} đã bị chặn vĩnh viễn/tạm thời tại Windows Firewall (Rule Blacklist).[cite: 2]")
    else:
        print(f"[-] Cảnh báo: Không thể khóa IP {ip_source} trên Windows Firewall (Hãy kiểm tra quyền Administrator).")

    # 2. Chuẩn bị payload báo động gửi sang Backend để lưu DB và kích hoạt WebSocket Real-time[cite: 2]
    payload = {
        "ip_source": ip_source,
        "attack_type": attack_type,
        "threshold_value": total_faults
    }
    
    # Đẩy vào hàng đợi bất đồng bộ để gọi API sang máy Giàu không làm nghẽn luồng đọc log[cite: 1]
    request_queue.put((BACKEND_URL, payload))

def parse_hmail_log_line(line_clean):
    """Phân tích cú pháp dòng log hMailServer, kiểm tra ngưỡng và kích hoạt cơ chế Zero-Trust[cite: 1]"""
    now = time.time()
    
    # Biểu thức Regex bóc tách cấu trúc log chuẩn Extended của hMailServer[cite: 1]
    # Mẫu: "POP3D" 13108 230 "2026-11-02 16:34:35.501" "10.20.0.147" "SENT: -ERR Invalid user name or password."
    log_pattern = r'^"([^"]+)"\s+\d+\s+\d+\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"'
    match = re.match(log_pattern, line_clean)
    
    if match:
        protocol, log_time, ip_source, log_message = match.groups()
        
        # Bỏ qua các kết nối từ vòng lặp nội bộ
        if ip_source in ["127.0.0.1", "::1"]:
            return

        # KỊCH BẢN 1: Phát hiện Brute-force mật khẩu (POP3D hoặc SMTPI)[cite: 1, 2]
        if "Invalid user name or password" in log_message or "Authentication failed" in log_message:
            auth_violations[ip_source] = clean_old_timestamps(auth_violations[ip_source])
            auth_violations[ip_source].append(now)
            
            total_faults = len(auth_violations[ip_source])
            print(f"[⚠️ WARNING] IP {ip_source} đăng nhập lỗi lần {total_faults}/60s")
            
            if total_faults > AUTH_FAIL_THRESHOLD:
                print(f"[🚨 CRITICAL] IP {ip_source} VƯỢT NGƯỠNG BRUTE-FORCE MẬT KHẨU!")
                trigger_alert_and_block(ip_source, "Brute-force Mật khẩu", total_faults)
                auth_violations[ip_source].clear()

        # KỊCH BẢN 2: Phát hiện Spam Mail / Directory Harvest Attack (Mã lỗi 550)[cite: 1, 2]
        elif "550 Unknown user" in log_message:
            spam_violations[ip_source] = clean_old_timestamps(spam_violations[ip_source])
            spam_violations[ip_source].append(now)
            
            total_spam_faults = len(spam_violations[ip_source])
            print(f"[⚠️ WARNING] IP {ip_source} kích hoạt mã lỗi 550 lần {total_spam_faults}/60s")
            
            if total_spam_faults > SPAM_FAIL_THRESHOLD:
                print(f"[🚨 CRITICAL] IP {ip_source} VƯỢT NGƯỠNG SPAM MAIL (SMTP ABUSE)!")
                trigger_alert_and_block(ip_source, "Spam Mail (SMTP Abuse)", total_spam_faults)
                spam_violations[ip_source].clear()


class MailLogHandler(FileSystemEventHandler):
    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.file_positions = {} # Lưu vị trí con trỏ file cuối cùng đã đọc

    def on_modified(self, event):
        # Chỉ xử lý file có phần mở rộng .log
        if not event.is_directory and event.src_path.endswith('.log'):
            self.read_new_lines(event.src_path)

    def read_new_lines(self, file_path):
        """Hàm đọc các dòng văn bản mới xuất hiện theo thời gian thực (Real-time Tail)[cite: 1]"""
        try:
            if file_path not in self.file_positions:
                # Đặt con trỏ ở cuối file để chỉ đọc các dòng log phát sinh sau khi khởi động
                self.file_positions[file_path] = os.path.getsize(file_path)
                return

            current_size = os.path.getsize(file_path)
            
            # Nếu file bị reset hoặc xóa nội dung (dung lượng nhỏ hơn vị trí cũ)
            if current_size < self.file_positions[file_path]:
                self.file_positions[file_path] = 0

            if current_size == self.file_positions[file_path]:
                return

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(self.file_positions[file_path])
                lines = f.readlines()
                self.file_positions[file_path] = f.tell()

            for line in lines:
                line_clean = line.strip()
                if line_clean:
                    # Phân tích dòng log qua bộ não NIDS Host-based
                    parse_hmail_log_line(line_clean)
                    
        except Exception as e:
            print(f"[-] Lỗi đọc file log: {e}")


def start_host_nids():
    path_to_watch = r"C:\Program Files (x86)\hMailServer\Logs"
    if not os.path.exists(path_to_watch):
        print(f"[-] Thư mục log không tồn tại: {path_to_watch}. Hãy kiểm tra lại đường dẫn hMailServer!")
        return

    print(f"[*] Module Host-based NIDS đang giám sát thư mục: {path_to_watch}")
    print(f"[*] Cơ chế Zero-Trust Enforcer đã được kích hoạt (Tự động chặn Windows Firewall khi vượt ngưỡng).[cite: 2]")
    event_handler = MailLogHandler(path_to_watch)
    
    # Sử dụng PollingObserver để đảm bảo bắt sự kiện ổn định trên Windows[cite: 1]
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    # Yêu cầu chạy Terminal / VS Code bằng quyền Administrator để tương tác Windows Firewall[cite: 1, 2]
    start_host_nids()
