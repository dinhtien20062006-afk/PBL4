# PBL4 NIDS Backend - Mail Security & Traffic Monitoring

Hệ thống phát hiện xâm nhập mạng (NIDS) và quản lý Firewall thời gian thực.

## 💻 Yêu cầu hệ thống
- Python 3.10+
- MySQL Server 8.0+ / phpMyAdmin
- Hệ điều hành: Windows 10/11 (Bắt buộc chạy bằng quyền Administrator để tương tác Firewall)

## 🛠️ Hướng dẫn cài đặt
1. **Thiết lập Cơ sở dữ liệu:**
   - Tạo database `pbl4_mail_nids` trong MySQL.
   - Nhập (Import) file `database_schema.sql` để tạo toàn bộ bảng, cấu trúc Index và Event Scheduler dọn log.
   - Cập nhật thông tin kết nối (user/mật khẩu) trong file `app/database.py`.

2. **Cài đặt môi trường Python:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt