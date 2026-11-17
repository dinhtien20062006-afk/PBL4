"""Đồng bộ 2 chiều Firewall máy chủ <-> Backend (Dashboard).

- Firewall có IP mà Dashboard chưa biết  -> báo lên Dashboard (hiện "Đã chặn").
- Dashboard bấm Chặn                     -> Engine chặn IP trên Firewall máy chủ.
- Dashboard bấm Bỏ chặn                  -> Engine gỡ IP khỏi Firewall máy chủ.
"""
import os
import time

import requests

import firewall_manager as fw

SYNC_URL = os.getenv("NIDS_API_BASE", "http://127.0.0.1:8000").rstrip("/") + "/api/blocked-ips/sync"
INTERVAL = 4  # giây
LOCAL_GRACE = 30  # giây: IP vừa được Engine tự chặn thì chưa gỡ (chờ cảnh báo kịp lên Backend)


def start_firewall_sync():
    print(f"[*] Đồng bộ 2 chiều Firewall <-> Backend mỗi {INTERVAL}s ({SYNC_URL})")
    first = True
    while True:
        try:
            ips = fw.get_current_blocked_ips()
            if first and ips is not None:
                print(f"[*] Firewall máy chủ hiện đang chặn: {ips if ips else 'chưa có IP nào'}")
                first = False
            if ips is not None:  # đọc Firewall lỗi thì bỏ qua lượt này, không báo sai
                r = requests.post(SYNC_URL, json={"ips": ips}, timeout=5)
                if not r.ok:
                    print(f"[-] Backend từ chối đồng bộ ({r.status_code}): {r.text}")
                else:
                    res = r.json()
                    if res.get("added"):
                        print(f"[+] Đã báo Dashboard các IP đang bị chặn: {res['added']}")
                    for ip in res.get("to_block", []):
                        print(f"[~] Dashboard yêu cầu chặn {ip}")
                        fw.block_ip(ip)
                    for ip in res.get("to_unblock", []):
                        if time.time() - fw.LAST_LOCAL_BLOCK.get(ip, 0) < LOCAL_GRACE:
                            continue
                        print(f"[~] Dashboard yêu cầu bỏ chặn {ip}")
                        fw.unblock_ip(ip)
        except requests.RequestException as e:
            print(f"[-] Không gọi được Backend ({SYNC_URL}): {e}")
        except Exception as e:
            print(f"[-] Lỗi đồng bộ Firewall: {e}")
        time.sleep(INTERVAL)
