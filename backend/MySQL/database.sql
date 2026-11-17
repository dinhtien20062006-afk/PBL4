-- PBL4 Mail NIDS — schema. Chạy: mysql -u root -p --default-character-set=utf8mb4 < database.sql
CREATE DATABASE IF NOT EXISTS pbl4_mail_nids CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pbl4_mail_nids;

-- 1. Thống kê gói tin: mỗi dòng = số gói của 1 IP nguồn trong 1 giây (do NIDS Engine gửi lên)
CREATE TABLE IF NOT EXISTS logs_traffic (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_source VARCHAR(45) NOT NULL,
    protocol VARCHAR(10) NOT NULL,
    packet_count INT NOT NULL,
    port_target SMALLINT UNSIGNED NOT NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_ip_source (ip_source),
    INDEX idx_traffic_cover (ip_source, timestamp, protocol, packet_count)
);

-- 2. Blacklist (status_active: 1 = đang chặn, 0 = đã gỡ)
CREATE TABLE IF NOT EXISTS blacklist_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    reason_blocked TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    unblocked_at DATETIME NULL,
    status_active TINYINT(1) DEFAULT 1,
    INDEX idx_ip_status (ip_address, status_active)
);

-- 3. Nhật ký tấn công
CREATE TABLE IF NOT EXISTS alert_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_source VARCHAR(45) NOT NULL,
    attack_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,              -- Low | Medium | High | Critical
    threshold_value INT NOT NULL,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_detected_at (detected_at),
    INDEX idx_alert_ip (ip_source)
);

-- 4. Quản trị viên
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. Cấu hình ngưỡng phát hiện (trang "Cấu hình")
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(50) PRIMARY KEY,
    config_value INT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
