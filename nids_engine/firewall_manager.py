import ipaddress
import json
import subprocess
import threading
import time

# Tên Rule Firewall cố định (tự tạo nếu chưa có)
RULE_NAME = "NIDS_Blacklist_Rule"

_lock = threading.Lock()
LAST_LOCAL_BLOCK = {}  # ip -> thời điểm Engine tự chặn gần nhất (để đồng bộ không gỡ nhầm)


def _ps(script: str) -> str:
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
         f"$ErrorActionPreference = 'Stop'; {script}"],
        capture_output=True, text=True, check=True, encoding="utf-8", errors="replace", timeout=20,
    )
    return result.stdout.strip()


def get_current_blocked_ips():
    """Danh sách IP đang nằm trong rule chặn (rule tắt hoặc không có -> rỗng)."""
    try:
        out = _ps(
            f"$r = Get-NetFirewallRule -DisplayName '{RULE_NAME}' -ErrorAction SilentlyContinue; "
            "if ($null -eq $r -or $r.Enabled -ne 'True') { '[]' } else { "
            "$a = @($r | Get-NetFirewallAddressFilter | Select-Object -ExpandProperty RemoteAddress "
            "| Where-Object { $_ -ne 'Any' -and $_ -ne '*' }); ConvertTo-Json -InputObject $a -Compress }"
        )
        data = json.loads(out or "[]")
        if isinstance(data, str):
            data = [data]
        return [str(x).split("/")[0] for x in data]
    except Exception as e:
        print(f"[-] Lỗi khi đọc danh sách IP từ Firewall (chạy bằng quyền Administrator?): {e}")
        return None  # None = không đọc được (khác với [] = rule rỗng)


def _apply(ip_address: str, add: bool) -> bool:
    ip = str(ipaddress.ip_address(ip_address))
    script = (
        f"$n = '{RULE_NAME}'; $ip = '{ip}'; $add = ${str(add).lower()}; "
        "$r = Get-NetFirewallRule -DisplayName $n -ErrorAction SilentlyContinue; "
        "if ($null -eq $r) { "
        "  if ($add) { New-NetFirewallRule -DisplayName $n -Direction Inbound -Action Block "
        "    -RemoteAddress @($ip) -Protocol Any -Profile Any -Enabled True | Out-Null }; return }; "
        "$cur = @($r | Get-NetFirewallAddressFilter | Select-Object -ExpandProperty RemoteAddress "
        "  | Where-Object { $_ -ne 'Any' -and $_ -ne '*' }); "
        "$new = @($cur | Where-Object { $_ -ne $ip }); "
        "if ($add) { $new = $new + $ip }; "
        "if ($new.Count -eq 0) { Set-NetFirewallRule -DisplayName $n -RemoteAddress 'Any'; "
        "  Disable-NetFirewallRule -DisplayName $n } "
        "else { Set-NetFirewallRule -DisplayName $n -RemoteAddress $new; Enable-NetFirewallRule -DisplayName $n }"
    )
    with _lock:
        _ps(script)
    return True


def block_ip(ip_address: str):
    """Chặn IP: thêm vào rule Blacklist (tự tạo rule nếu chưa có)."""
    try:
        _apply(ip_address, True)
        LAST_LOCAL_BLOCK[ip_address] = time.time()
        print(f"[+] Đã chặn IP {ip_address} trên Windows Firewall.")
        return True
    except Exception as e:
        err = getattr(e, "stderr", None) or e
        print(f"[-] Không chặn được {ip_address} (cần quyền Administrator): {str(err).strip()}")
        return False


def unblock_ip(ip_address: str):
    """Gỡ chặn IP. Rule rỗng thì tắt rule (tránh rule Block 'Any' chặn toàn bộ)."""
    try:
        _apply(ip_address, False)
        print(f"[*] Đã gỡ chặn IP {ip_address} trên Windows Firewall.")
        return True
    except Exception as e:
        err = getattr(e, "stderr", None) or e
        print(f"[-] Không gỡ chặn được {ip_address}: {str(err).strip()}")
        return False
