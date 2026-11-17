import axios from 'axios'

export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
export const WS_URL = import.meta.env.VITE_WS_URL || API_BASE.replace(/^http/, 'ws') + '/ws/monitoring'

const http = axios.create({ baseURL: API_BASE, timeout: 8000 })

// Mọi endpoint của FastAPI nằm ở đây — component không tự gọi axios/fetch.

// Firewall Blacklist
export const getBlockedIPs = () => http.get('/api/blocked-ips')
// Chặn/gỡ chặn gọi PowerShell nhiều lần phía server nên có thể chậm hơn 8 giây của http chung.
const FIREWALL_TIMEOUT = 30000
export const blockIP = (ip, reason, alertId) =>
  http.post('/api/blocked-ips', { ip_address: ip, reason, alert_id: alertId ?? null }, { timeout: FIREWALL_TIMEOUT })
export const unblockIP = (ip) =>
  http.post('/api/blocked-ips/unblock', { ip_address: ip }, { timeout: FIREWALL_TIMEOUT })

// Cảnh báo & IP đang theo dõi
export const getAlerts = (limit = 100) => http.get('/api/alerts', { params: { limit } })
export const getIPs = () => http.get('/api/ips')

// Thống kê lưu lượng
export const getOverview = () => http.get('/api/stats/overview')
export const getTrafficSeries = (minutes = 30) => http.get('/api/stats/traffic', { params: { minutes } })
export const getProtocols = () => http.get('/api/stats/protocols')
export const getPorts = () => http.get('/api/stats/ports')
export const getTopSources = (limit = 5) => http.get('/api/stats/top-sources', { params: { limit } })
export const getRecentLogs = (limit = 8) => http.get('/api/logs/recent', { params: { limit } })

// Attack Lab — chạy/dừng kịch bản giả lập tấn công qua API, không cần mở Terminal
export const getAttackStatus = () => http.get('/api/attack/status')
export const startAttack = (scriptId, params = {}) => http.post(`/api/attack/${scriptId}/start`, params)
export const stopAttack = (scriptId) => http.post(`/api/attack/${scriptId}/stop`)

// Cấu hình ngưỡng
export const getThresholds = () => http.get('/api/config/thresholds')
export const saveThresholds = (values) => http.put('/api/config/thresholds', values)

// Lấy thông báo lỗi dễ đọc từ response của FastAPI
// `detail` có thể là chuỗi (HTTPException) hoặc mảng object (lỗi 422) — render mảng sẽ làm sập React.
export const errorMessage = (e, fallback) => {
  const detail = e?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length) return detail.map((d) => d?.msg).filter(Boolean).join('; ') || fallback
  if (e?.code === 'ECONNABORTED') return 'Backend phản hồi quá lâu. Kiểm tra lại danh sách sau vài giây.'
  return fallback
}
