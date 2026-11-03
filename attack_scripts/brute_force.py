import poplib
import time

# Điền chính xác IP máy tính của Tiên (Mail Server)
SERVER_IP = "10.20.0.147"  # Thay bằng IP thực tế của Tiên
PORT = 110
TARGET_EMAIL = "user01@company.local"

def run_brute_force():
    print(f"[!] Bắt đầu kịch bản giả lập Brute-force tới: {TARGET_EMAIL}")
    count = 0
    
    # Giả lập vòng lặp tấn công liên tục gửi mật khẩu sai
    while True:
        try:
            count += 1
            # Kết nối tới dịch vụ POP3 Mail Server của Tiên
            client = poplib.POP3(SERVER_IP, PORT, timeout=2)
            
            # Gửi Username
            client.user(TARGET_EMAIL)
            
            # Gửi Password sai ngẫu nhiên để kích hoạt mã lỗi trong log của Tiên
            fake_password = f"wrong_pass_{count}"
            client.pass_(fake_password)
            
            client.quit()
        except poplib.error_proto as e:
            # hMailServer từ chối xác thực và sinh log "Authentication failed"
            print(f"[+] Lượt {count}: Đã bắn kết nối lỗi -> {e}")
        except Exception as e:
            print(f"[-] Lỗi kết nối mạng: {e}")
            
        # Nghỉ 0.2 giây mỗi lượt để tránh làm treo hoàn toàn máy 4GB RAM của bạn
        time.sleep(0.2)

if __name__ == "__main__":
    run_brute_force()
