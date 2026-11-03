import subprocess
import re

# Tên Rule Firewall cố định đã tạo ở Bước 2 (Đảm bảo tên này trùng khớp hoàn toàn với Windows Defender Firewall)
RULE_NAME = "NIDS_Blacklist_Rule"

def get_current_blocked_ips():
    """Hàm lấy danh sách các IP hiện đang bị chặn trong Rule"""
    try:
        # Gọi lệnh PowerShell để lấy danh sách RemoteAddress của Rule
        cmd = f"Get-NetFirewallRule -DisplayName '{RULE_NAME}' | Get-NetFirewallAddressFilter"
        result = subprocess.run(
            ["powershell", "-Command", cmd], 
            capture_output=True, 
            text=True, 
            check=True,
            encoding="utf-8", 
            errors="ignore"
        )
        
        output = result.stdout
        # Tìm dòng chứa RemoteAddress
        for line in output.split('\n'):
            if "RemoteAddress" in line:
                ips_raw = line.split(":")[-1].strip()
                if not ips_raw or ips_raw == "Any":
                    return []
                # Tách các IP ra thành một mảng (PowerShell trả về dạng mảng cách nhau bởi dấu phẩy hoặc khoảng trắng)
                ips = [ip.strip() for ip in re.split(r'[,\s]+', ips_raw) if ip.strip()]
                return ips
        return []
    except subprocess.CalledProcessError as e:
        print(f"[-] Lỗi khi đọc danh sách IP từ Firewall: {e}")
        return []

def block_ip(ip_address: str):
    """Hàm chặn IP vi phạm: Thêm IP vào danh sách RemoteAddress của Rule Blacklist"""
    try:
        current_ips = get_current_blocked_ips()
        
        # Nếu IP này đã nằm trong danh sách chặn rồi thì bỏ qua
        if ip_address in current_ips:
            print(f"[!] IP {ip_address} đã bị chặn từ trước trên Firewall.")
            return True
            
        current_ips.append(ip_address)
        # Chuyển mảng IP thành chuỗi định dạng cho PowerShell (ví dụ: '192.168.1.50','10.0.0.5')
        ips_str = ",".join([f"'{ip}'" for ip in current_ips])
        
        # Lệnh PowerShell cập nhật lại danh sách RemoteAddress cho Rule
        cmd = f"Set-NetFirewallRule -DisplayName '{RULE_NAME}' -RemoteAddress {ips_str}"
        subprocess.run(["powershell", "-Command", cmd], check=True, encoding="utf-8", errors="ignore")
        print(f"[+] Tự động khóa IP thành công: Chặn hoàn toàn kết nối từ IP -> {ip_address}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Thất bại! Vui lòng kiểm tra xem bạn đã chạy VS Code với quyền Administrator chưa. Chi tiết: {e}")
        return False

def unblock_ip(ip_address: str):
    """Hàm gỡ chặn IP (Phục vụ cho tính năng Unblock từ Backend của Giàu)"""
    try:
        current_ips = get_current_blocked_ips()
        
        if ip_address not in current_ips:
            print(f"[!] IP {ip_address} không tồn tại trong danh sách chặn của Firewall.")
            return True
            
        current_ips.remove(ip_address)
        
        # Nếu danh sách trống, đưa về trạng thái "Any" để tránh lỗi PowerShell không nhận chuỗi rỗng
        if not current_ips:
            cmd = f"Set-NetFirewallRule -DisplayName '{RULE_NAME}' -RemoteAddress Any"
        else:
            ips_str = ",".join([f"'{ip}'" for ip in current_ips])
            cmd = f"Set-NetFirewallRule -DisplayName '{RULE_NAME}' -RemoteAddress {ips_str}"
            
        subprocess.run(["powershell", "-Command", cmd], check=True, encoding="utf-8", errors="ignore")
        print(f"[*] Giải phóng IP thành công: Đã gỡ chặn IP -> {ip_address}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Lỗi khi gỡ chặn IP: {e}")
        return False

# Đoạn mã chạy thử nghiệm cục bộ (Kiểm thử thủ công)
if __name__ == "__main__":
    test_ip = "192.168.1.50"
    print(f"[~] Đang tiến hành chạy thử nghiệm chặn IP: {test_ip}...")
    block_ip(test_ip)
