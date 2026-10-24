import random
from datetime import datetime, timezone
import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dữ liệu mẫu mặc định
_ips_db = [
    {"ip": "192.168.1.14", "status": "normal", "proto": "TCP", "packets": 1284, "lastSeen": "2 giây trước", "blocked": False},
    {"ip": "10.0.0.82", "status": "suspicious", "proto": "TCP", "packets": 9531, "lastSeen": "5 giây trước", "blocked": False},
]

_PROTOCOLS = ["TCP", "UDP", "ICMP"]


def get_db_connection():
    """Kết nối tới MySQL của XAMPP."""
    return pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="",
        database="pbl4_nids",
        cursorclass=pymysql.cursors.DictCursor,
    )


def fetch_mysql_blocked_ips():
    """Đọc danh sách IP bị chặn từ bảng blocked_ips trong MySQL."""
    mysql_ips = []
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT ip_address, attack_type FROM blocked_ips ORDER BY id DESC")
            rows = cursor.fetchall()
            for row in rows:
                mysql_ips.append({
                    "ip": row["ip_address"],
                    "status": "suspicious",
                    "proto": f"TCP ({row['attack_type']})",
                    "packets": random.randint(1500, 15000),
                    "lastSeen": "Vừa phát hiện",
                    "blocked": True,
                })
        conn.close()
    except Exception as e:
        print(f"[!] Chưa đọc được MySQL (đang dùng RAM tạm): {e}")
    return mysql_ips


def _random_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def _random_packet_log() -> dict:
    return {
        "id": f"{datetime.now(timezone.utc).timestamp()}-{random.randint(0, 99999)}",
        "src_ip": _random_ip(),
        "dst_ip": _random_ip(),
        "port": random.choice([25, 110, 443, 80] + [random.randint(1024, 65535)]),
        "protocol": random.choice(_PROTOCOLS),
        "time": "vừa xong",
    }


@app.get("/")
def read_root():
    return {"status": "NIDS & Mail Server System Running", "mode": "Zero-Trust Active"}


@app.get("/api/logs/recent")
def list_recent_logs(limit: int = 20):
    limit = max(1, min(limit, 100))
    return [_random_packet_log() for _ in range(limit)]


@app.get("/api/ips")
def list_ips():
    """Gộp danh sách IP từ MySQL (do 3 script giả lập đẩy vào) và IP mẫu."""
    db_ips = fetch_mysql_blocked_ips()
    existing = {item["ip"] for item in db_ips}
    combined = db_ips + [row for row in _ips_db if row["ip"] not in existing]
    return combined


@app.get("/api/alerts/recent")
def list_recent_alerts(limit: int = 20):
    """Danh sách cảnh báo gần đây cho AlertsTable.jsx (Frontend - Quyền).

    Tạm thời dựng từ bảng blocked_ips (do các script trong attack_scripts/
    ghi vào khi NIDS Engine của Tiên phát hiện tấn công). Khi nids_engine có
    bảng alerts riêng (với port/severity thật), thay nguồn dữ liệu ở đây.
    """
    limit = max(1, min(limit, 100))
    alerts = []
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Chỉ dùng id/ip_address/attack_type — cùng cột với
            # fetch_mysql_blocked_ips() ở trên, tránh giả định cột timestamp
            # chưa chắc đã có trong schema MySQL hiện tại.
            cursor.execute(
                "SELECT id, ip_address, attack_type FROM blocked_ips "
                "ORDER BY id DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
        conn.close()
        for row in rows:
            attack_type = row.get("attack_type", "")
            port = 110 if "pop3" in attack_type.lower() or "brute" in attack_type.lower() else 25
            alerts.append({
                "id": row["id"],
                "ip": row["ip_address"],
                "type": attack_type,
                "port": port,
                "sev": "high" if "syn" in attack_type.lower() or "flood" in attack_type.lower() else "med",
                "time": "vừa phát hiện",
            })
    except Exception as e:
        print(f"[!] /api/alerts/recent: chưa đọc được MySQL: {e}")
    return alerts


@app.get("/api/blocked-ips")
def list_blocked_ips():
    """Trả về tất cả IP đang bị chặn (từ MySQL + RAM)."""
    return [row for row in list_ips() if row["blocked"]]


@app.post("/api/ips/{ip}/block")
def block_ip(ip: str):
    for row in _ips_db:
        if row["ip"] == ip:
            row["blocked"] = True
            return row
    raise HTTPException(status_code=404, detail="IP not found")


@app.post("/api/ips/{ip}/unblock")
def unblock_ip(ip: str):
    # Xóa khỏi bảng blocked_ips trong MySQL nếu có
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM blocked_ips WHERE ip_address = %s", (ip,))
        conn.commit()
        conn.close()
    except Exception:
        pass

    for row in _ips_db:
        if row["ip"] == ip:
            row["blocked"] = False
            return row
    return {"ip": ip, "blocked": False}