import smtplib
from email.mime.text import MIMEText
import time
import sys

# ==========================================
# CẤU HÌNH THÔNG SỐ KẾT NỐI HMAILSERVER
# ==========================================
TARGET_IP = "127.0.0.1"  # Địa chỉ IP của Mail Server (hoặc IP VPN khi test qua mạng ảo)
TARGET_PORT = 25         # Cổng SMTP mặc định
SENDER = "client@pbl4.local"    # Tài khoản gửi đã cấu hình trên hMailServer
RECEIVER = "admin@pbl4.local"   # Tài khoản nhận
EMAIL_COUNT = 100        # Tổng số lượng email muốn bắn liên tục
DELAY = 0.05             # Độ trễ giữa các lần gửi (giây) để tạo mật độ lưu lượng

def send_smtp_traffic():
    print(f"[*] Đang khởi tạo kịch bản gửi mail tự động tới mục tiêu: {TARGET_IP}:{TARGET_PORT}")
    print(f"[*] Người gửi: {SENDER} | Người nhận: {RECEIVER}\n")
    
    success_count = 0

    for i in range(1, EMAIL_COUNT + 1):
        try:
            # Soạn nội dung gói tin email đơn giản
            msg = MIMEText(f"Payload kiểm thử lưu lượng mạng PBL4 - Gói số #{i}")
            msg['Subject'] = f"PBL4 Traffic Test #{i}"
            msg['From'] = SENDER
            msg['To'] = RECEIVER

            # Thiết lập kết nối SMTP không bảo mật tới Server cục bộ
            server = smtplib.SMTP(TARGET_IP, TARGET_PORT, timeout=3)
            server.sendmail(SENDER, [RECEIVER], msg.as_string())
            server.quit()
            
            success_count += 1
            sys.stdout.write(f"\r[+] Đã gửi thành công {success_count}/{EMAIL_COUNT} gói tin SMTP...")
            sys.stdout.flush()
            
            # Nghỉ một nhịp nhỏ để điều chỉnh tốc độ dòng dữ liệu
            time.sleep(DELAY)
            
        except ConnectionRefusedError:
            print(f"\n\n[!!!] KẾT NỐI BỊ TỪ CHỐI TẠI GÓI TIN SỐ {i}.")
            print("[✓] Nguyên nhân: Module NIDS đã phát hiện lưu lượng bất thường và Firewall đã tiến hành chặn IP.")
            break
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "10060" in error_msg:
                print(f"\n\n[!!!] TIMEOUT TẠI GÓI TIN SỐ {i}.")
                print("[✓] Nguyên nhân: Tường lửa hoặc hệ thống phòng thủ Zero-Trust đã drop các gói tin từ IP này.")
            else:
                print(f"\n[!] Lỗi phát sinh ở gói tin {i}: {e}")
            break
            
    print("\n[*] Quá trình tạo lưu lượng mạng đã kết thúc.")

if __name__ == '__main__':
    send_smtp_traffic()