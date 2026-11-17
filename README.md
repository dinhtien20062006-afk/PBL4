# PBL4 – Mail NIDS Dashboard (React + FastAPI + MySQL)

```
PBL4-NIDS/
├── backend/                FastAPI
│   ├── app/
│   │   ├── main.py         khởi tạo app, CORS, WebSocket /ws/monitoring
│   │   ├── config.py       biến môi trường (.env), ngưỡng mặc định
│   │   ├── database.py     kết nối MySQL (SQLAlchemy)
│   │   ├── models.py       bảng DB      schemas.py  payload request
│   │   ├── serializers.py  DB -> JSON    firewall.py Windows Firewall
│   │   ├── ws_manager.py
│   │   └── routers/        alerts · blocked_ips · logs · stats · config
│   └── MySQL/              database.sql (schema) · sample_data.sql (dữ liệu mẫu)
├── frontend/               React + Vite
│   └── src/
│       ├── api/            MỌI lời gọi API + WebSocket URL (1 chỗ duy nhất)
│       ├── hooks/          usePolling · useMonitoringWebSocket · useNidsData
│       ├── components/     thành phần dùng lại (+ file .css cùng tên)
│       ├── pages/          Dashboard · Traffic · Alerts · IpManagement · Config · AttackLab
│       └── utils/format.js
├── nids_engine/            main_core.py = network_nids (SYN Flood) + host_nids (log hMailServer)
└── attack_scripts/         script kiểm thử
```

## Chạy
1. **DB**: `mysql -u root -p --default-character-set=utf8mb4 < backend/MySQL/database.sql`
   (tuỳ chọn, để xem giao diện ngay: `... < backend/MySQL/sample_data.sql`)
2. **Backend** (cổng 8000):
   ```
   cd backend
   python -m venv venv && venv\Scripts\activate      (Linux/Mac: source venv/bin/activate)
   pip install -r requirements.txt
   copy .env.example .env                             (điền DB_PASSWORD nếu có)
   uvicorn app.main:app --reload --port 8000
   ```
   Kiểm tra http://127.0.0.1:8000/ → `"database_connected": true` · Swagger: `/docs`.
   Chặn/bỏ chặn IP thật trên Windows Firewall cần chạy bằng **Administrator**; trên Linux/Mac backend tự
   chuyển sang chế độ chỉ ghi DB (`FIREWALL_ENABLED=false`).
3. **Frontend** (cổng 5173): `cd frontend && npm install && npm run dev` (hoặc `run_frontend.bat`).
   Backend ở máy khác → sửa `frontend/.env` (`VITE_API_BASE_URL`, `VITE_WS_URL`).
4. **NIDS Engine** (tuỳ chọn, cần Npcap + quyền Admin): `cd nids_engine && python main_core.py`.
   Backend ở máy khác: đặt biến môi trường `NIDS_API_BASE=http://<ip-backend>:8000`.

## Luồng dữ liệu
Engine ─POST→ `/api/logs/traffic`, `/api/alerts/trigger` ─→ MySQL ─→ Dashboard.
Dashboard làm mới mỗi 5 giây **và** nhận đẩy realtime qua WebSocket (`new_alert`, `ip_blocked`, `ip_unblocked`, `traffic_tick`).

## API
| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | /api/alerts?limit= | Lịch sử cảnh báo |
| POST | /api/alerts/trigger | Engine gửi cảnh báo `{ip_source, attack_type, severity?, threshold_value?}` |
| GET / POST | /api/blocked-ips | Danh sách IP đang chặn / chặn IP `{ip_address, reason}` |
| POST | /api/blocked-ips/unblock (alias /api/unblock) | Bỏ chặn `{ip_address}` |
| GET | /api/ips | IP đang theo dõi (tổng hợp logs_traffic + alert + blacklist) |
| GET | /api/stats/overview · traffic · protocols · ports · top-sources | Thống kê Dashboard |
| GET | /api/logs/recent | Gói tin mới nhất |
| POST | /api/logs/traffic (alias /ingest) | Engine gửi thống kê gói tin `{ip_source, packet_count, port_target, protocol?}` |
| POST | /api/logs/traffic/batch | Engine gửi nhiều bản ghi trong 1 request `{items:[…]}` |
| WS | /ws/monitoring | Đẩy realtime: `new_alert` · `ip_blocked` · `ip_unblocked` · `traffic_tick` (2 giây/lần) |
| GET / PUT | /api/config/thresholds | Đọc / lưu ngưỡng phát hiện (bảng system_config) |

## Lỗi thường gặp
- Banner đỏ "Không kết nối được Backend": chưa chạy FastAPI/MySQL, hoặc sai `DB_PASSWORD`.
- CORS: thêm origin vào `CORS_ORIGINS` trong `backend/.env`.
- Tiếng Việt lỗi font: import SQL với `--default-character-set=utf8mb4`.
- Biểu đồ trống: chưa có gói tin trong khoảng thời gian chọn → chạy engine hoặc nạp `sample_data.sql`.

## Ghi chú tối ưu giao diện (frontend)

- **Realtime không giật**: cảnh báo từ WebSocket được gom theo đợt 0,4 giây rồi chèn vào danh sách tại chỗ; số liệu tổng nạp lại tối đa 1 lần / 1,5 giây; toast cảnh báo được gom thành 1 thông báo tổng hợp khi có bão (`src/utils/alertToasts.js`).
- **Tốc độ gói tin/giây** nằm trong store riêng (`useLivePps`) nên mỗi 2 giây chỉ 4 thẻ KPI render lại, không phải cả trang.
- **`usePolling`**: bỏ qua dữ liệu không đổi, tạm dừng khi tab bị ẩn, không chạy chồng request.
- **Danh sách dài** (cảnh báo, IP) render theo đợt 30–50 dòng + nút "Hiển thị thêm"; thẻ cảnh báo dùng `content-visibility: auto`.
- **Màu sắc**: bảng màu và biến CSS ở `src/index.css`; màu biểu đồ ở `src/utils/theme.js`. Mọi cặp chữ/nền đạt tương phản WCAG AA (≥ 4.5:1).

## Thay đổi ở đợt tối ưu kết nối Backend ↔ Frontend
- **Hợp nhất backend về `app/routers`**: `main.py` trước đây import thư mục `routers/` cũ (thiếu schema, không khớp frontend); bản cũ được chuyển vào `_old_backup/` (có thể xoá).
- Bổ sung `BlockRequest`, `IpRequest`, `TrafficBatch`, `ThresholdsUpdate`, model `SystemConfig`, cột `unblocked_at` còn thiếu → chặn/bỏ chặn IP, lưu ngưỡng chạy được.
- **WebSocket `traffic_tick`** được phát thật (trước đó backend không phát nên thẻ "Gói tin / giây" không realtime); broadcast song song, tự loại client chết.
- **Múi giờ**: thời gian trả về kèm offset (`+07:00`) nên "x phút trước" luôn đúng dù server/engine ở múi giờ khác; models dùng giờ local thống nhất với truy vấn thống kê (trước đây `utcnow` làm biểu đồ lệch 7 giờ).
- Biểu đồ lưu lượng bỏ phút đang dở (hết "rơi dốc về 0" ở điểm cuối), cửa sổ căn theo phút tròn.
- CORS đọc từ `.env`, tự cho phép máy trong mạng LAN; bật nén GZip.
- **Engine** đọc địa chỉ backend từ biến môi trường `NIDS_API_BASE` (trước đây hardcode URL có khoảng trắng `http:// 192…` nên không gửi được).
- Frontend: header mobile không còn chồng chéo (ô lọc xuống hàng riêng); trang phụ lazy-load, tách chunk biểu đồ (bundle chính 753 kB → 323 kB).
