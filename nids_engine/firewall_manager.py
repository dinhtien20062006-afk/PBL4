import os
import subprocess

def block_ip(ip_address: str):
    """
    Thêm luật chặn toàn bộ lưu lượng Inbound từ IP vi phạm bằng lệnh netsh.
    """
    rule_name = f"PBL4_Block_{ip_address}"
    # Lệnh netsh để chặn IP
    command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip_address}'
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"[SUCCESS] Đã chặn thành công IP: {ip_address}")
        else:
            print(f"[ERROR] Không thể chặn IP {ip_address}. Lỗi: {result.stderr.strip()}")
    except Exception as e:
        print(f"[EXCEPTION] Lỗi khi thực thi lệnh block IP: {e}")

def unblock_ip(ip_address: str):
    """
    Xóa luật chặn IP khỏi Windows Defender Firewall.
    """
    rule_name = f"PBL4_Block_{ip_address}"
    command = f'netsh advfirewall firewall delete rule name="{rule_name}"'
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"[SUCCESS] Đã gỡ chặn (unblock) thành công IP: {ip_address}")
        else:
            print(f"[ERROR] Không thể gỡ chặn IP {ip_address}. Lỗi: {result.stderr.strip()}")
    except Exception as e:
        print(f"[EXCEPTION] Lỗi khi thực thi lệnh unblock IP: {e}")

if __name__ == "__main__":
    # Test thử nghiệm thủ công
    test_ip = "192.168.1.100"
    print(f"--- Đang kiểm tra thêm rule chặn cho IP: {test_ip} ---")
    block_ip(test_ip)
    
    input("Nhấn Enter để tiến hành xóa rule test...")
    unblock_ip(test_ip)
