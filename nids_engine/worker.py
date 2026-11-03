import queue
import threading

import requests

API_URL = "http://127.0.0.1:8000/api/logs/ingest"

# Hàng đợi tạm trong RAM: sniffer (producer) đẩy vào, worker (consumer) gửi lên Backend
log_queue = queue.Queue(maxsize=10000)


def db_writer_worker():
    while True:
        try:
            packet_data = log_queue.get(timeout=2)
        except queue.Empty:
            continue
        try:
            requests.post(API_URL, json=packet_data, timeout=5)
        except Exception as e:
            print(f"Lỗi ghi log: {e}")
        finally:
            log_queue.task_done()


threading.Thread(target=db_writer_worker, daemon=True).start()


def log_queue_join():
    """Chờ gửi hết các gói còn trong hàng đợi trước khi thoát."""
    log_queue.join()
