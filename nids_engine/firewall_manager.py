import sys
from pathlib import Path

repository_root = str(Path(__file__).resolve().parents[1])
if repository_root not in sys.path:
    sys.path.insert(0, repository_root)

from backend.app.firewall import block_ip, get_current_blocked_ips, unblock_ip

__all__ = ["block_ip", "get_current_blocked_ips", "unblock_ip"]


if __name__ == "__main__":
    test_ip = "192.168.1.50"
    print(f"Testing Windows Firewall block for {test_ip}...")
    block_ip(test_ip)
