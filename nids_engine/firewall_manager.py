import subprocess
import json

# Tên Rule Firewall cố định đã tạo ở Bước 2
RULE_NAME = "NIDS_Blacklist_Rule"

def get_current_blocked_ips():
    """Hàm lấy danh sách các IP hiện đang bị chặn trong Rule bằng cách trả về JSON từ PowerShell"""
    try:
        ps_script = f"""
        $rule = Get-NetFirewallRule -DisplayName '{RULE_NAME}' -ErrorAction SilentlyContinue
        if ($null -eq $rule) {{
            Write-Output "[]"
            exit
        }}
        $filter = Get-NetFirewallAddressFilter -AssociatedNetFirewallRule $rule
        $addrs = $filter.RemoteAddress
        if ($null -eq $addrs -or $addrs -eq '*') {{
            Write-Output "[]"
        }} else {{
            # Lọc bỏ dấu * hoặc Any nếu có, chỉ giữ lại các IP hợp lệ
            $list = @($addrs) | Where-Object {{ $_ -ne '*' -and $_ -ne 'Any' }}
            ConvertTo-Json @($list) -Compress
        }}
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        output = result.stdout.strip()
        if not output:
            return []
            
        # Parse dữ liệu JSON trả về từ PowerShell thành mảng Python
        ips = json.loads(output)
        if isinstance(ips, str):
            return [ips]
        return list(ips)
        
    except Exception as e:
        print(f"[-] Lỗi khi đọc danh sách IP từ Firewall: {e}")
        return []

def block_ip(ip_address: str):
    """Hàm chặn IP vi phạm: Thêm IP vào danh sách RemoteAddress của Rule Blacklist"""
    try:
        current_ips = get_current_blocked_ips()
        
        # Nếu IP này đã nằm trong danh sách chặn rồi thì bỏ qua
        if ip_address in current_ips:
            print(f"[!] IP {ip_address} đã bị chặn từ trước.")
            return True
            
        current_ips.append(ip_address)
        
        # Tạo mảng chuỗi định dạng cho PowerShell (ví dụ: @('192.168.1.50','10.0.0.5'))
        ips_formatted = ",".join([f"'{ip}'" for ip in current_ips])
        
        ps_script = f"""
        Set-NetFirewallRule -DisplayName '{RULE_NAME}' -RemoteAddress @({ips_formatted})
        Write-Output "SUCCESS"
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if "SUCCESS" in result.stdout:
            print(f"[+] Tự động khóa IP thành công: Chặn hoàn toàn kết nối từ IP -> {ip_address}")
            return True
        else:
            print(f"[-] Lỗi khi cập nhật Firewall: {result.stderr.strip()}")
            return False
            
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else str(e)
        print(f"[-] Thất bại! Vui lòng kiểm tra xem bạn đã chạy VS Code với quyền Administrator chưa. Chi tiết: {err_msg}")
        return False

def unblock_ip(ip_address: str):
    """Hàm gỡ chặn IP (Phục vụ cho tính năng Unblock từ Backend của Giàu)"""
    try:
        current_ips = get_current_blocked_ips()
        
        if ip_address not in current_ips:
            print(f"[!] IP {ip_address} không tồn tại trong danh sách chặn.")
            return True
            
        current_ips.remove(ip_address)
        
        # Nếu danh sách trống, đưa về trạng thái "Any" (*) để tránh lỗi
        if not current_ips:
            ps_script = f"""
            Set-NetFirewallRule -DisplayName '{RULE_NAME}' -RemoteAddress Any
            Write-Output "SUCCESS"
            """
        else:
            ips_formatted = ",".join([f"'{ip}'" for ip in current_ips])
            ps_script = f"""
            Set-NetFirewallRule -DisplayName '{RULE_NAME}' -RemoteAddress @({ips_formatted})
            Write-Output "SUCCESS"
            """
            
        result = subprocess.run(
            ["powershell", "-Command", ps_script], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if "SUCCESS" in result.stdout:
            print(f"[*] Giải phóng IP thành công: Đã gỡ chặn IP -> {ip_address}")
            return True
        else:
            print(f"[-] Lỗi khi gỡ chặn IP: {result.stderr.strip()}")
            return False
            
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else str(e)
        print(f"[-] Lỗi khi gỡ chặn IP: {err_msg}")
        return False

# Đoạn mã chạy thử nghiệm cục bộ (Kiểm thử thủ công)
if __name__ == "__main__":
    # Thử nghiệm chặn một IP giả định để kiểm tra tính năng
    test_ip = "192.168.1.49"
    print(f"[~] Đang tiến hành chạy thử nghiệm chặn IP: {test_ip}...")
    block_ip(test_ip)
