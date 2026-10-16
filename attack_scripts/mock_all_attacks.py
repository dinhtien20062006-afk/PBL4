import pymysql
import time
import random

# Hàm kết nối tới MySQL của XAMPP
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='',
        database='pbl4_nids'
    )

def trigger_alert(attack_name):
    # Sinh ngẫu nhiên IP của kẻ tấn công giả định
    hacker_ip = f"{random.randint(11, 200)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    print(f"\n[*] NIDS đang phân tích gói tin...")
    time.sleep(1.5)
    print(f"[!] KÍCH HOẠT ZERO-TRUST: Thuật toán NIDS đã bắt quả tang hành vi {attack_name}")
    print(f"[*] Kẻ tấn công đến từ IP: {hacker_ip}")
    print("[*] Đang ghi log cảnh báo vào Database và ra lệnh cho Firewall...")
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Đẩy thông tin cảnh báo vào MySQL
            sql = "INSERT INTO blocked_ips (ip_address, attack_type) VALUES (%s, %s)"
            cursor.execute(sql, (hacker_ip, attack_name))
        conn.commit()
        conn.close()
        print("[+] Thành công! Mở Web Dashboard để xem IP đã bị cập nhật lên bảng đen.")
    except Exception as e:
        print(f"[x] Lỗi khi kết nối MySQL XAMPP: {e}")

if __name__ == '__main__':
    while True:
        print("\n==============================================")
        print("   TRÌNH GIẢ LẬP CẢNH BÁO NIDS ZERO-TRUST     ")
        print("==============================================")
        print("1. Giả lập thuật toán chặn SYN Flood")
        print("2. Giả lập thuật toán chặn Brute Force POP3/SMTP")
        print("3. Giả lập thuật toán chặn Spam Mail (Rate Limit)")
        print("4. Thoát")
        
        choice = input("\n[?] Chọn kịch bản tấn công muốn NIDS bắt (1-4): ")
        
        if choice == '1':
            trigger_alert("TCP SYN Flood Attack")
        elif choice == '2':
            trigger_alert("Password Brute Force")
        elif choice == '3':
            trigger_alert("SMTP Spam / L7 Flood")
        elif choice == '4':
            print("Đang thoát...")
            break
        else:
            print("Vui lòng chọn từ 1 đến 4.")
        
        time.sleep(2)