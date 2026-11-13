CREATE DATABASE pbl4_mail_nids;
USE pbl4_mail_nids;


-- 1. Bảng logs_traffic (Lưu thông tin thống kê gói tin)
CREATE TABLE logs_traffic (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,       -- Dùng BIGINT vì bảng log sẽ tăng dữ liệu cực kỳ nhanh
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_source VARCHAR(45) NOT NULL,
    protocol VARCHAR(10) NOT NULL,              -- MỚI: Ghi nhận giao thức (TCP, UDP, ICMP...)
    packet_count INT NOT NULL,
    port_target SMALLINT UNSIGNED NOT NULL,     -- TỐI ƯU: Chỉ chiếm 2 bytes, lưu giới hạn port (0 - 65535)
    
    -- Đánh chỉ mục (Index) để tối ưu truy xuất dữ liệu cho Dashboard
    INDEX idx_timestamp (timestamp),
    INDEX idx_ip_source (ip_source)
);

-- 2. Bảng blacklist_ips (Quản lý trạng thái chặn IP)
CREATE TABLE blacklist_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    reason_blocked TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status_active TINYINT(1) DEFAULT 1,         -- 1 là đang chặn, 0 là đã mở khóa
    
    -- Composite Index giúp truy vấn nhanh khi kiểm tra "IP này có đang bị chặn không?"
    INDEX idx_ip_status (ip_address, status_active)
);

-- 3. Bảng alert_history (Nhật ký tấn công)
CREATE TABLE alert_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_source VARCHAR(45) NOT NULL,
    attack_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,              -- MỚI: Phân loại cảnh báo (Low, Medium, High, Critical)
    threshold_value INT NOT NULL,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_detected_at (detected_at)         -- Index để lọc lịch sử tấn công theo ngày/tháng nhanh hơn
);

-- 4. Bảng quản trị viên (users)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);