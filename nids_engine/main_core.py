import threading
from network_nids import start_network_sniff
from host_nids import start_host_nids

if __name__ == "__main__":
    print("=== KHỞI CHẠY CORE HYBRID NIDS ENGINE (PBL4) ===")
    
    # Khởi tạo 2 luồng độc lập chạy song song
    network_thread = threading.Thread(target=start_network_sniff, daemon=True)
    host_thread = threading.Thread(target=start_host_nids, daemon=True)
    
    network_thread.start()
    host_thread.start()
    
    # Giữ luồng chính luôn sống
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[-] Đang tắt hệ thống giám sát NIDS.")
