import axios from 'axios'

// Instance axios dùng chung, trỏ tới FastAPI (Backend của Giàu).
// Đổi bằng VITE_API_BASE_URL trong frontend/.env nếu Backend chạy chỗ khác.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 8000,
})

// ---- Firewall Blacklist (bảng blocked_ips) ----
export const getBlockedIPs = () => api.get('/api/blocked-ips')
export const blockIP = (ip, reason, alertId) =>
  api.post('/api/blocked-ips', { ip_address: ip, reason, alert_id: alertId ?? null })
export const unblockIP = (ip) => api.post('/api/blocked-ips/unblock', { ip_address: ip })

// ---- Cảnh báo (bảng alerts) ----
export const getAlerts = (limit = 100) => api.get('/api/alerts', { params: { limit } })

// ---- IP đang theo dõi (tổng hợp từ traffic_logs) ----
export const getIPs = () => api.get('/api/ips')

// ---- Thống kê lưu lượng (từ traffic_logs) ----
export const getOverview = () => api.get('/api/stats/overview')
export const getTrafficSeries = (minutes = 30) => api.get('/api/stats/traffic', { params: { minutes } })
export const getProtocols = () => api.get('/api/stats/protocols')
export const getPorts = () => api.get('/api/stats/ports')
export const getTopSources = (limit = 5) => api.get('/api/stats/top-sources', { params: { limit } })
export const getRecentLogs = (limit = 8) => api.get('/api/logs/recent', { params: { limit } })

export default api
