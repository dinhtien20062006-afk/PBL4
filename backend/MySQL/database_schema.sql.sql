-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 16, 2026 at 09:10 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pbl4_mail_nids`
--

-- --------------------------------------------------------

--
-- Table structure for table `alert_history`
--

CREATE TABLE `alert_history` (
  `id` int(11) NOT NULL,
  `ip_source` varchar(45) NOT NULL,
  `attack_type` varchar(50) NOT NULL,
  `severity` varchar(20) NOT NULL,
  `threshold_value` int(11) NOT NULL,
  `detected_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alert_history`
--

INSERT INTO `alert_history` (`id`, `ip_source`, `attack_type`, `severity`, `threshold_value`, `detected_at`) VALUES
(1, '203.0.113.45', 'SYN Flood', 'Critical', 100, '2026-11-16 06:23:14'),
(2, '10.0.0.50', 'Brute-force', 'High', 5, '2026-11-16 06:52:16'),
(3, '203.0.113.99', 'SYN Flood', 'Critical', 100, '2026-11-16 07:00:55'),
(4, '203.0.113.99', 'SYN Flood', 'Critical', 100, '2026-11-16 07:09:05'),
(5, '203.0.113.99', 'SYN Flood', 'Critical', 100, '2026-11-16 07:09:24'),
(6, '203.0.113.99', 'SYN Flood', 'Critical', 100, '2026-11-16 07:12:14');

-- --------------------------------------------------------

--
-- Table structure for table `attack_thresholds`
--

CREATE TABLE `attack_thresholds` (
  `id` int(11) NOT NULL,
  `attack_type` varchar(50) NOT NULL,
  `threshold_limit` int(11) NOT NULL,
  `time_window_seconds` int(11) NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attack_thresholds`
--

INSERT INTO `attack_thresholds` (`id`, `attack_type`, `threshold_limit`, `time_window_seconds`, `is_active`, `updated_at`) VALUES
(1, 'SYN Flood', 500, 2, 1, '2026-11-16 06:35:33'),
(2, 'Brute-force', 5, 60, 1, '2026-11-16 12:24:12'),
(3, 'Spam', 20, 60, 1, '2026-11-16 12:24:12');

-- --------------------------------------------------------

--
-- Table structure for table `blacklist_ips`
--

CREATE TABLE `blacklist_ips` (
  `id` int(11) NOT NULL,
  `ip_address` varchar(45) NOT NULL,
  `reason_blocked` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `status_active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `blacklist_ips`
--

INSERT INTO `blacklist_ips` (`id`, `ip_address`, `reason_blocked`, `created_at`, `status_active`) VALUES
(1, '192.168.1.50', 'Phát hiện tấn công dò mật khẩu (Brute-force)', '2026-11-16 06:00:28', 0),
(3, '192.168.1.200', 'Chặn để test tính năng gỡ chặn', '2026-11-16 07:35:05', 0);

-- --------------------------------------------------------

--
-- Table structure for table `logs_traffic`
--

CREATE TABLE `logs_traffic` (
  `id` bigint(20) NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `ip_source` varchar(45) NOT NULL,
  `protocol` varchar(10) NOT NULL,
  `packet_count` int(11) NOT NULL,
  `port_target` smallint(5) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `logs_traffic`
--

INSERT INTO `logs_traffic` (`id`, `timestamp`, `ip_source`, `protocol`, `packet_count`, `port_target`) VALUES
(1, '2026-11-16 05:42:30', '192.168.1.10', 'TCP', 246, 8080),
(2, '2026-11-16 06:48:43', '192.168.1.100', 'TCP', 45, 443);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT 'admin',
  `last_login` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alert_history`
--
ALTER TABLE `alert_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_detected_at` (`detected_at`),
  ADD KEY `idx_alert_ip` (`ip_source`),
  ADD KEY `idx_alert_time` (`detected_at`);

--
-- Indexes for table `attack_thresholds`
--
ALTER TABLE `attack_thresholds`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `attack_type` (`attack_type`);

--
-- Indexes for table `blacklist_ips`
--
ALTER TABLE `blacklist_ips`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_ip_status` (`ip_address`,`status_active`),
  ADD KEY `idx_blacklist_ip` (`ip_address`);

--
-- Indexes for table `logs_traffic`
--
ALTER TABLE `logs_traffic`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_timestamp` (`timestamp`),
  ADD KEY `idx_ip_source` (`ip_source`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `alert_history`
--
ALTER TABLE `alert_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `attack_thresholds`
--
ALTER TABLE `attack_thresholds`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `blacklist_ips`
--
ALTER TABLE `blacklist_ips`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `logs_traffic`
--
ALTER TABLE `logs_traffic`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

DELIMITER $$
--
-- Events
--
CREATE DEFINER=`root`@`localhost` EVENT `purge_old_logs` ON SCHEDULE EVERY 12 HOUR STARTS '2026-11-16 15:04:07' ON COMPLETION NOT PRESERVE ENABLE DO DELETE FROM logs_traffic 
    WHERE created_at < NOW() - INTERVAL 1 DAY$$

DELIMITER ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
