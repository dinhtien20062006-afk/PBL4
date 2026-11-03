-- Dữ liệu thử cho giao diện (chạy sau database.sql)
USE pbl4_mail_nids;

INSERT INTO traffic_logs (source_ip, dest_ip, port, protocol, packet_size, status) VALUES
('192.168.1.14',  '10.0.0.5', 25,  'TCP',  512,  'Normal'),
('192.168.1.14',  '10.0.0.5', 110, 'TCP',  256,  'Normal'),
('10.0.0.82',     '10.0.0.5', 25,  'TCP',  1400, 'Alert'),
('10.0.0.82',     '10.0.0.5', 25,  'TCP',  1400, 'Alert'),
('172.16.4.201',  '10.0.0.5', 53,  'UDP',  90,   'Normal'),
('203.0.113.55',  '10.0.0.5', 22,  'TCP',  60,   'Alert'),
('203.0.113.55',  '10.0.0.5', 22,  'TCP',  60,   'Alert'),
('198.51.100.9',  '10.0.0.5', 25,  'TCP',  800,  'Alert');

INSERT INTO alerts (traffic_log_id, attack_type, source_ip, severity) VALUES
(3, 'Spam Mail',       '10.0.0.82',    'High'),
(6, 'Brute Force SSH', '203.0.113.55', 'High');

INSERT INTO blocked_ips (alert_id, ip_address, reason, status) VALUES
(2, '203.0.113.55', 'Brute Force SSH', 'Blocked');
