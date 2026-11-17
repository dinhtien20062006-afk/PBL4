import ipaddress
import json
import logging
import subprocess
import threading

RULE_NAME = "NIDS_Blacklist_Rule"
logger = logging.getLogger(__name__)


class FirewallError(RuntimeError):
    pass


class FirewallRuleNotFound(FirewallError):
    pass


def _run_powershell(script: str) -> str:
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                f"$ErrorActionPreference = 'Stop'; {script}",
            ],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise FirewallError(
            detail or f"PowerShell exited with status {exc.returncode}."
        ) from exc
    except (OSError, subprocess.SubprocessError) as exc:
        raise FirewallError(f"Windows Firewall command failed: {exc}") from exc
    return result.stdout.strip()


def get_current_blocked_ips() -> list[str]:
    script = (
        f"$rule = Get-NetFirewallRule -DisplayName '{RULE_NAME}' "
        "-ErrorAction SilentlyContinue; "
        "if ($null -eq $rule) { "
        "ConvertTo-Json -InputObject @{ exists = $false; addresses = @() } -Compress "
        "} else { "
        "$addresses = @($rule | Get-NetFirewallAddressFilter -ErrorAction Stop "
        "| Select-Object -ExpandProperty RemoteAddress); "
        "ConvertTo-Json -InputObject @{ exists = $true; addresses = $addresses } -Compress "
        "}"
    )
    output = _run_powershell(script)
    if not output:
        raise FirewallError("Windows Firewall returned an empty address list.")

    try:
        rule = json.loads(output)
    except json.JSONDecodeError as exc:
        raise FirewallError("Could not parse the Windows Firewall address list.") from exc

    if not isinstance(rule, dict) or not isinstance(rule.get("exists"), bool):
        raise FirewallError("Windows Firewall returned an invalid rule response.")
    if not rule["exists"]:
        raise FirewallRuleNotFound(f"Firewall rule '{RULE_NAME}' was not found.")

    addresses = rule.get("addresses")
    if addresses is None or addresses == "Any":
        return []
    if isinstance(addresses, str):
        addresses = [addresses]
    if not isinstance(addresses, list) or not all(isinstance(item, str) for item in addresses):
        raise FirewallError("Windows Firewall returned an invalid address list.")
    if "Any" in addresses:
        return []
    return addresses


def _set_blocked_ips(addresses: list[str]) -> None:
    canonical_addresses = [str(ipaddress.ip_address(address)) for address in addresses]
    if not canonical_addresses:
        _run_powershell(
            f"Disable-NetFirewallRule -DisplayName '{RULE_NAME}' -ErrorAction Stop; "
            f"Set-NetFirewallRule -DisplayName '{RULE_NAME}' "
            "-RemoteAddress 'Any' -ErrorAction Stop"
        )
        return

    address_list = ",".join(f"'{address}'" for address in canonical_addresses)
    script = (
        f"Set-NetFirewallRule -DisplayName '{RULE_NAME}' "
        f"-RemoteAddress @({address_list}) -ErrorAction Stop; "
        f"Enable-NetFirewallRule -DisplayName '{RULE_NAME}' -ErrorAction Stop"
    )
    _run_powershell(script)


_lock = threading.Lock()  # các thao tác sửa rule phải chạy lần lượt (đọc-sửa-ghi cùng 1 rule)


def _apply(ip_address: str, add: bool) -> bool:
    """Thêm/bớt 1 IP khỏi rule bằng ĐÚNG 1 lần gọi PowerShell (trước đây 4 lần ≈ 5-8 giây)."""
    address = str(ipaddress.ip_address(ip_address))
    script = (
        f"$n = '{RULE_NAME}'; $ip = '{address}'; $add = ${str(add).lower()}; "
        "$r = Get-NetFirewallRule -DisplayName $n -ErrorAction SilentlyContinue; "
        "if ($null -eq $r) { "
        "  if ($add) { New-NetFirewallRule -DisplayName $n -Direction Inbound -Action Block "
        "    -RemoteAddress @($ip) -Protocol Any -Profile Any -Enabled True | Out-Null }; "
        "  return }; "
        "$cur = @($r | Get-NetFirewallAddressFilter | Select-Object -ExpandProperty RemoteAddress "
        "  | Where-Object { $_ -ne 'Any' }); "
        "$new = @($cur | Where-Object { $_ -ne $ip }); "
        "if ($add) { $new = $new + $ip }; "
        "if ($new.Count -eq 0) { "
        "  Set-NetFirewallRule -DisplayName $n -RemoteAddress 'Any'; Disable-NetFirewallRule -DisplayName $n "
        "} else { "
        "  Set-NetFirewallRule -DisplayName $n -RemoteAddress $new; Enable-NetFirewallRule -DisplayName $n }"
    )
    with _lock:
        _run_powershell(script)
    return True


def block_ip(ip_address: str) -> bool:
    try:
        return _apply(ip_address, True)
    except (ValueError, FirewallError) as exc:
        logger.error("Could not block IP %s in Windows Firewall: %s", ip_address, exc)
        return False


def unblock_ip(ip_address: str) -> bool:
    try:
        return _apply(ip_address, False)
    except (ValueError, FirewallError) as exc:
        logger.error("Could not unblock IP %s in Windows Firewall: %s", ip_address, exc)
        return False


def is_ip_blocked(ip_address: str) -> bool:
    try:
        address = str(ipaddress.ip_address(ip_address))
        try:
            return address in get_current_blocked_ips()
        except FirewallRuleNotFound:
            return False
    except (ValueError, FirewallError) as exc:
        logger.error("Could not check IP %s in Windows Firewall: %s", ip_address, exc)
        return False
