# PBL4 – Mail NIDS Dashboard (React + FastAPI + MySQL)

Dashboard lấy **dữ liệu thật từ MySQL**: Firewall Blacklist, Cảnh báo, Danh sách IP, Lưu lượng.

```
PBL4-NIDS/
├── backend/            FastAPI (Giàu)   app/, routers/, MySQL/database.sql
├── frontend/           React + Vite + Tailwind (Quyền)
├── nids_engine/        sniffer.py + worker.py (bắt gói tin thật -> MySQL)
└── attack_scripts/     placeholder kiểm thử
```

## Yêu cầu
Python 3.10+, Node.js 18+, MySQL 8 hoặc MariaDB (XAMPP, MySQL Workbench… đều được).

## 1. Tạo database + dữ liệu mẫu
```
mysql -u root -p --default-character-set=utf8mb4 < backend/MySQL/database.sql
```
Hoặc Workbench / phpMyAdmin: mở `backend/MySQL/database.sql` -> Execute.
File tự DROP/CREATE database `pbl4_mail_nids`, tạo 6 bảng và nạp dữ liệu mẫu (500 traffic_logs, 6 alerts, 6 blocked_ips).

Kiểm tra: `SELECT ip_address, reason, status FROM blocked_ips;` -> 5 dòng `Blocked`, 1 dòng `Unblocked`.

## 2. Chạy Backend (cổng 8000)
```
cd backend
python -m venv venv
venv\Scripts\activate            (Linux/Mac: source venv/bin/activate)
pip install -r ../requirements.txt
copy .env.example .env           (Linux/Mac: cp .env.example .env)
```
Mở `backend/.env`, điền `DB_PASSWORD` nếu MySQL của bạn có mật khẩu (XAMPP mặc định để trống).
```
uvicorn app.main:app --reload --port 8000
```
Kiểm tra: http://127.0.0.1:8000/ phải có `"database_connected": true`.
Swagger: http://127.0.0.1:8000/docs — thử `GET /api/blocked-ips`.

## 3. Chạy Frontend (cổng 3000)
```
cd frontend
npm install
npm run dev
```
Mở http://localhost:3000 -> menu **"IP bị chặn"** -> bảng **Firewall Blacklist** hiển thị đúng các dòng `status='Blocked'` trong MySQL.

- **Bỏ chặn / Unblock**: `POST /api/blocked-ips/unblock` -> DB đổi `status='Unblocked'`, ghi `unblocked_at`.
- **Chặn IP** (ở trang Cảnh báo / bảng IP): `POST /api/blocked-ips` -> thêm dòng mới vào `blocked_ips`.
- Dữ liệu tự làm mới mỗi 5 giây.

(Backend ở địa chỉ khác: copy `frontend/.env.example` thành `frontend/.env`, sửa `VITE_API_BASE_URL`.)

## 4. (Tuỳ chọn) Ghi gói tin thật vào MySQL
Backend phải đang chạy. Windows cần cài Npcap và mở terminal bằng quyền Administrator:
```
pip install -r requirements.txt
cd nids_engine
python sniffer.py
```
Gói tin mới sẽ xuất hiện ở trang **Lưu lượng** (biểu đồ, Packet feed).

## API
| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | /api/blocked-ips | IP đang bị chặn (blocked_ips, status=Blocked) |
| POST | /api/blocked-ips | Chặn IP `{ip_address, reason, alert_id}` |
| POST | /api/blocked-ips/unblock | Gỡ chặn `{ip_address}` |
| GET | /api/alerts | Cảnh báo (kèm cổng, join traffic_logs) |
| GET | /api/ips | IP đang theo dõi (tổng hợp traffic_logs) |
| GET | /api/stats/overview, /traffic, /protocols, /ports, /top-sources | Thống kê cho Dashboard |
| GET | /api/logs/recent | Gói tin mới nhất |
| POST | /api/logs/ingest | NIDS Engine gửi gói tin vào DB |

## Lỗi thường gặp
- **Bảng báo "Không tải được danh sách IP bị chặn"**: Backend chưa chạy, hoặc `database_connected` = false (sai mật khẩu trong `backend/.env`).
- **Lỗi CORS**: frontend phải chạy ở cổng 3000 hoặc 5173 (đã cho phép trong `backend/app/main.py`). Cổng khác thì thêm vào `allow_origins`.
- **Tiếng Việt bị lỗi font trong bảng**: import lại `database.sql` với `--default-character-set=utf8mb4`.
- **Biểu đồ Lưu lượng trống**: dữ liệu mẫu tính theo giờ lúc import (khoảng 1 giờ gần nhất). Import lại file SQL hoặc chạy sniffer để có dữ liệu mới.

## Chưa dùng dữ liệu SQL
- Trang **Cấu hình** (ngưỡng phát hiện) vẫn lưu trên giao diện, vì database chưa có bảng cấu hình.
- Trang **Attack Lab** chỉ là trang thông tin.
