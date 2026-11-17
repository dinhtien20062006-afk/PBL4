-- Dữ liệu mẫu để xem giao diện khi chưa chạy NIDS Engine (chạy SAU database.sql)
USE pbl4_mail_nids;

INSERT INTO alert_history (ip_source, attack_type, severity, threshold_value, detected_at) VALUES
('203.0.113.44',  'SYN Flood',        'High',     312, NOW() - INTERVAL 2 MINUTE),
('198.51.100.9',  'Brute-force POP3', 'Medium',    8,  NOW() - INTERVAL 11 MINUTE),
('192.0.2.171',   'Spam Mail (SMTP)', 'Medium',    74, NOW() - INTERVAL 26 MINUTE),
('203.0.113.201', 'Brute-force SMTP', 'High',      15, NOW() - INTERVAL 40 MINUTE),
('198.51.100.63', 'SYN Flood',        'Low',       58, NOW() - INTERVAL 1 HOUR);

INSERT INTO blacklist_ips (ip_address, reason_blocked, status_active) VALUES
('203.0.113.44',  'SYN Flood (cảnh báo #1)', 1),
('203.0.113.201', 'Brute-force SMTP (cảnh báo #4)', 1),
('198.51.100.63', 'SYN Flood — đã gỡ', 0);

-- ~600 dòng traffic trong 30 phút gần nhất
INSERT INTO logs_traffic (timestamp, ip_source, protocol, packet_count, port_target)
SELECT NOW() - INTERVAL (n.i * 3) SECOND,
       ELT(1 + (n.i MOD 6), '192.168.1.14','10.0.0.82','172.16.4.201','203.0.113.44','198.51.100.9','192.168.1.27'),
       ELT(1 + (n.i MOD 5), 'TCP','TCP','TCP','UDP','ICMP'),
       5 + (n.i * 7 MOD 90),
       ELT(1 + (n.i MOD 4), 25, 25, 110, 587)
FROM (SELECT a.N + b.N * 10 + c.N * 100 AS i
      FROM (SELECT 0 N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
           (SELECT 0 N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
           (SELECT 0 N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) c) n;
