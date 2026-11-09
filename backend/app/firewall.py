import ipaddress
import json
import logging
import subprocess

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


def block_ip(ip_address: str) -> bool:
    try:
        address = str(ipaddress.ip_address(ip_address))
        try:
            current_ips = get_current_blocked_ips()
        except FirewallRuleNotFound:
            address_list = f"@('{address}')"
            _run_powershell(
                f"New-NetFirewallRule -DisplayName '{RULE_NAME}' "
                "-Direction Inbound -Action Block "
                f"-RemoteAddress {address_list} "
                "-Protocol Any -Profile Any -Enabled True -ErrorAction Stop"
            )
            return address in get_current_blocked_ips()

        if address not in current_ips:
            _set_blocked_ips([*current_ips, address])
        return address in get_current_blocked_ips()
    except (ValueError, FirewallError) as exc:
        logger.error("Could not block IP %s in Windows Firewall: %s", ip_address, exc)
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


def unblock_ip(ip_address: str) -> bool:
    try:
        address = str(ipaddress.ip_address(ip_address))
        current_ips = get_current_blocked_ips()
        if address not in current_ips:
            if not current_ips:
                _set_blocked_ips([])
            return address not in get_current_blocked_ips()
        _set_blocked_ips([item for item in current_ips if item != address])
        return address not in get_current_blocked_ips()
    except (ValueError, FirewallError) as exc:
        logger.error("Could not unblock IP %s in Windows Firewall: %s", ip_address, exc)
        return False
