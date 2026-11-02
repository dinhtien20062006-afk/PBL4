import queue
import threading
import time
import requests

# Khởi tạo Queue toàn cục để chứa các gói tin chưa kịp lưu
log_queue = queue.Queue(maxsize=10000) # Lưu tạm tối đa 10k gói tin trong RAM

def db_writer_worker():
    """Luồng Consumer: Chạy ngầm liên tục để lấy data từ Queue và gửi API"""
    while True:
        try:
            # Lấy gói tin ra khỏi hàng đợi (timeout để luồng không bị kẹt vĩnh viễn)
            packet_data = log_queue.get(timeout=2)
            
            # Gửi sang Backend API để lưu (hoặc Insert trực tiếp bằng DB Pool)
            requests.post("http://127.0.0.1:8000/api/logs/ingest", json=packet_data)
            
            log_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Lỗi ghi log: {e}")

# Khởi động luồng Worker chạy ngầm (Daemon)
worker_thread = threading.Thread(target=db_writer_worker, daemon=True)
worker_thread.start()

def packet_sniffer_callback(packet):
    """Luồng Producer: Giả lập hàm bắt gói tin của Tiên"""
    data = {
        "source_ip": packet.src,
        "dest_ip": packet.dst,
        "port": 80,
        "protocol": "TCP",
        "packet_size": len(packet),
        "status": "Normal"
    }
    # Chỉ đẩy vào Queue (tốn 0.001s) rồi quay lại bắt gói tin tiếp theo ngay lập tức
    try:
        log_queue.put_nowait(data)
    except queue.Full:
        print("Cảnh báo: Queue đã đầy, hệ thống đang bị quá tải!")