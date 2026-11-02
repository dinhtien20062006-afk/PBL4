-- Tạo và sử dụng database mới
CREATE DATABASE pbl4_mail_nids;
USE pbl4_mail_nids;

-- 1. Bảng quản trị viên (users)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    last_login DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng tập luật phát hiện (detection_rules)
CREATE TABLE detection_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    description TEXT,
    protocol VARCHAR(20),
    match_pattern VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) DEFAULT 'alert',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng traffic_logs (Lưu lượng mạng)
CREATE TABLE traffic_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(45) NOT NULL,
    dest_ip VARCHAR(45) NOT NULL,
    port INT,
    protocol VARCHAR(20),
    packet_size INT,
    status VARCHAR(50)
);

-- 4. Bảng chi tiết giao dịch Mail (mail_transactions)
CREATE TABLE mail_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    traffic_log_id INT NOT NULL,
    sender VARCHAR(255),
    receiver VARCHAR(255),
    subject TEXT,
    has_attachment BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (traffic_log_id) REFERENCES traffic_logs(id) ON DELETE CASCADE
);

-- 5. Bảng alerts (Cảnh báo)
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_id INT, -- Liên kết với bảng detection_rules
    traffic_log_id INT, -- Liên kết với bảng traffic_logs
    attack_type VARCHAR(100) NOT NULL,
    source_ip VARCHAR(45) NOT NULL,
    severity VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES detection_rules(id) ON DELETE SET NULL,
    FOREIGN KEY (traffic_log_id) REFERENCES traffic_logs(id) ON DELETE CASCADE
);

-- 6. Bảng blocked_ips (IP bị chặn)
CREATE TABLE blocked_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_id INT, -- Liên kết với bảng alerts
    ip_address VARCHAR(45) NOT NULL,
    reason TEXT,
    blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    unblocked_at DATETIME NULL,
    status VARCHAR(50),
    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE SET NULL
);