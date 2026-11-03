# PBL4 – Mail NIDS Dashboard (React + FastAPI + MySQL)

Dashboard lấy **dữ liệu thật từ MySQL**: Firewall Blacklist, Cảnh báo, Danh sách IP, Lưu lượng.

```
PBL4-NIDS/
├── backend/            FastAPI (Giàu)  -> app/, routers/, MySQL/database.sql
├── frontend/           React + Vite + Tailwind (Quyền)
├── nids_engine/        sniffer.py + worker.py (bắt gói tin thật -> MySQL)
└── attack_scripts/     placeholder kiểm thử
```

## Yêu cầu
Python 3.10+, Node.js 18+, MySQL 8 / MariaDB (XAMPP, MySQL Workbench... đều được).

## 1. Tạo database + dữ liệu mẫu
Chạy file `backend/MySQL/database.sql` (tự DROP/CREATE database `pbl4_mail_nids`, tạo 6 bảng và nạp dữ liệu mẫu).

Dòng lệnh:
```
mysql -u root -p --default-character-set=utf8mb4 < backend/MySQL/database.sql
```
Hoặc dùng Workbench/phpMyAdmin: mở file -> Execute (file đã có `SET NAMES utf8mb4`).
Kiểm tra: `SELECT * FROM blocked_ips;` -> 6 dòng (5 `Blocked`, 1 `Unblocked`).

## 2. Chạy Backend (cổng 8000)
```
cd backend
python -m venv venv
venv\Scripts\activate            (Linux/Mac: source venv/bin/activate)
pip install -r ../requirements.txt
copy .env.example .env           (Linux/Mac: cp .env.example .env)   # sửa DB_PASSWORD nếu MySQL có mật khẩu
uvicorn app.main:app --reload --port 8000
```
Kiểm tra: http://127.0.0.1:8000/ phải có `"database_connected": true`
Swagger: http://127.0.0.1:8000/docs — thử http://127.0.0.1:8000/api/blocked-ips

## 3. Chạy Frontend (cổng 5173)
```
cd frontend
npm install
npm run dev
```
Mở http://localhost:5173 -> menu **"IP bị chặn"** -> bảng **Firewall Blacklist** hiển thị đúng các dòng `status='Blocked'` trong MySQL.
Nút **Bỏ chặn / Unblock** gọi `POST /api/blocked-ips/unblock` và cập nhật `status='Unblocked'`, `unblocked_at` trong DB.

(Backend ở địa chỉ khác: copy `frontend/.env.example` thành `.env` và sửa `VITE_API_BASE_URL`.)

## 4. (Tuỳ chọn) Ghi gói tin thật vào MySQL
Backend phải đang chạy. Windows cần cài Npcap, chạy terminal bằng quyền Administrator:
```
python nids_engine/sniffer.py 200
```
Các gói tin mới sẽ xuất hiện ở trang Lưu lượng / Packet feed.

## API
| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | /api/blocked-ips | IP đang bị chặn (bảng blocked_ips) |
| POST | /api/blocked-ips | Chặn IP `{ip_address, reason, alert_id}` |
| POST | /api/blocked-ips/unblock | Gỡ chặn `{ip_address}` |
| GET | /api/alerts | Danh sách cảnh báo (bảng alerts) |
| GET | /api/ips | IP đang theo dõi (tổng hợp từ traffic_logs) |
| GET | /api/stats/{overview,traffic,protocols,ports,top-sources} | Thống kê lưu lượng |
| GET | /api/logs/recent | Gói tin mới nhất |
| POST | /api/logs/ingest | Sniffer gửi gói tin vào DB |

## CORS (Bước 3)
Đã cấu hình `CORSMiddleware` trong `backend/app/main.py`, cho phép origin `localhost/127.0.0.1` cổng 5173 và 3000.

## Lưu ý
- Dữ liệu mẫu dùng `NOW()` lúc import nên biểu đồ lưu lượng (60 phút gần nhất) có dữ liệu ngay; sau 1 giờ hãy import lại hoặc chạy sniffer.
- Trang **Cấu hình** (ngưỡng) và **Attack Lab** chưa có bảng MySQL tương ứng nên vẫn là phần giao diện.
- `users.password_hash` trong dữ liệu mẫu chỉ là chỗ giữ chỗ, chưa có đăng nhập.
