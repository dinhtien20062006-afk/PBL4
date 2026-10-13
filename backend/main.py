from fastapi import FastAPI, HTTPException
from database import Database

app = FastAPI(
    title="PBL4 Mail NIDS API",
    description="Hệ thống API quản lý logs, cảnh báo, luật và IP bị chặn cho NIDS",
    version="1.0.0"
)

def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """Hàm hỗ trợ kết nối DB, thực thi truy vấn và trả về kết quả dạng JSON"""
    db = Database()
    conn = db.connect()
    if not conn:
        raise HTTPException(status_code=500, detail="Không thể kết nối đến cơ sở dữ liệu MySQL")
    
    try:
        # dictionary=True giúp kết quả trả về dạng Dict (tương thích trực tiếp với JSON của FastAPI)
        cursor = conn.cursor(dictionary=True) 
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
            
        return result
    except Exception as e:
        print(f"Lỗi truy vấn SQL: {e}")
        raise HTTPException(status_code=500, detail="Lỗi thực thi truy vấn cơ sở dữ liệu")
    finally:
        db.disconnect()

# ==========================================
# 1. API QUẢN LÝ LOG LƯU LƯỢNG (TRAFFIC LOGS)
# ==========================================
@app.get("/api/logs", tags=["Traffic Logs"])
def get_traffic_logs(limit: int = 50):
    """Lấy danh sách log lưu lượng mạng gần nhất (Mặc định 50 dòng)"""
    query = "SELECT * FROM traffic_logs ORDER BY timestamp DESC LIMIT %s"
    data = execute_query(query, (limit,))
    return {"status": "success", "total": len(data), "data": data}

# ==========================================
# 2. API QUẢN LÝ IP BỊ CHẶN (BLOCKED IPS)
# ==========================================
@app.get("/api/blocked-ips", tags=["Blocked IPs"])
def get_blocked_ips():
    """Lấy danh sách các IP đang bị chặn"""
    query = "SELECT * FROM blocked_ips ORDER BY blocked_at DESC"
    data = execute_query(query)
    return {"status": "success", "total": len(data), "data": data}

# ==========================================
# 3. API QUẢN LÝ CẢNH BÁO (ALERTS)
# ==========================================
@app.get("/api/alerts", tags=["Alerts"])
def get_alerts(limit: int = 50):
    """Lấy danh sách cảnh báo tấn công, kết hợp với tên luật từ bảng detection_rules"""
    query = """
        SELECT a.id, a.attack_type, a.source_ip, a.severity, a.created_at, 
               r.rule_name, t.dest_ip, t.port
        FROM alerts a
        LEFT JOIN detection_rules r ON a.rule_id = r.id
        LEFT JOIN traffic_logs t ON a.traffic_log_id = t.id
        ORDER BY a.created_at DESC LIMIT %s
    """
    data = execute_query(query, (limit,))
    return {"status": "success", "total": len(data), "data": data}

# ==========================================
# 4. API QUẢN LÝ LUẬT PHÁT HIỆN (DETECTION RULES)
# ==========================================
@app.get("/api/rules", tags=["Detection Rules"])
def get_detection_rules(active_only: bool = True):
    """Lấy danh sách các tập luật phát hiện. Mặc định chỉ lấy các luật đang kích hoạt (is_active = TRUE)"""
    if active_only:
        query = "SELECT * FROM detection_rules WHERE is_active = TRUE ORDER BY created_at DESC"
    else:
        query = "SELECT * FROM detection_rules ORDER BY created_at DESC"
        
    data = execute_query(query)
    return {"status": "success", "total": len(data), "data": data}

# ==========================================
# 5. API QUẢN LÝ GIAO DỊCH MAIL (MAIL TRANSACTIONS)
# ==========================================
@app.get("/api/mail-transactions", tags=["Mail Transactions"])
def get_mail_transactions(limit: int = 50):
    """Lấy thông tin chi tiết các giao dịch Mail (người gửi, người nhận, tiêu đề)"""
    query = """
        SELECT m.id, m.sender, m.receiver, m.subject, m.has_attachment, 
               t.timestamp, t.source_ip, t.dest_ip
        FROM mail_transactions m
        INNER JOIN traffic_logs t ON m.traffic_log_id = t.id
        ORDER BY t.timestamp DESC LIMIT %s
    """
    data = execute_query(query, (limit,))
    return {"status": "success", "total": len(data), "data": data}

# Kiểm tra trạng thái Server
@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "OK", "message": "NIDS Backend Server đang hoạt động!"}