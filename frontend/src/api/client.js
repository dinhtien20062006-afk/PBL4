import axios from 'axios'

// Đổi bằng biến môi trường VITE_API_BASE_URL khi deploy (mặc định: FastAPI local).
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 5000,
})

// ---------------------------------------------------------------------------
// Các endpoint dự kiến phía Backend (FastAPI + MySQL) — theo mục 2 & 5 trong
// mô tả đề tài. Hiện backend/main.py mới chỉ có route "/", nên các hàm dưới
// đây CHƯA được gọi ở bất kỳ đâu — chúng chỉ là khung sẵn để cắm vào khi
// backend hoàn thiện. Bật dần từng hàm và thay lệnh gọi mock tương ứng
// trong src/data/mockData.js hoặc trong component.
// ---------------------------------------------------------------------------

export async function fetchTrafficSummary() {
  // GET /api/traffic/summary -> { pps, protocol_breakdown, port_activity }
  const { data } = await api.get('/api/traffic/summary')
  return data
}

export async function fetchRecentLogs(limit = 20) {
  // GET /api/logs/recent -> N gói tin gần nhất NIDS Engine vừa bắt được
  // (IP nguồn, IP đích, cổng, giao thức, thời điểm). Dùng cho TrafficTable.jsx,
  // polling bằng setInterval cho tới khi thay bằng WebSocket (connectTrafficSocket).
  const { data } = await api.get('/api/logs/recent', { params: { limit } })
  return data
}

export async function fetchAlerts() {
  // GET /api/alerts -> danh sách cảnh báo NIDS (mới nhất trước)
  const { data } = await api.get('/api/alerts')
  return data
}

export async function fetchRecentAlerts(limit = 20) {
  // GET /api/alerts/recent -> dùng riêng cho AlertsTable.jsx (mục 2, phần
  // Quyền phụ trách). Trả về mảng { id, ip, type, port, sev, time } giống
  // SEED_ALERTS trong data/mockData.js. Khi backend (Tiên) chưa dựng route
  // này, AlertsTable.jsx tự rơi về dữ liệu mẫu, không chặn UI.
  const { data } = await api.get('/api/alerts/recent', { params: { limit } })
  return data
}

export async function fetchIps() {
  // GET /api/ips -> danh sách IP đang theo dõi + trạng thái block
  const { data } = await api.get('/api/ips')
  return data
}

export async function fetchBlockedIps() {
  // GET /api/blocked-ips -> chỉ những IP đã bị Zero-Trust Enforcer chặn
  const { data } = await api.get('/api/blocked-ips')
  return data
}

export async function blockIp(ip) {
  // POST /api/ips/{ip}/block -> Zero-Trust Enforcer gọi netsh advfirewall
  const { data } = await api.post(`/api/ips/${ip}/block`)
  return data
}

export async function unblockIp(ip) {
  // POST /api/ips/{ip}/unblock
  const { data } = await api.post(`/api/ips/${ip}/unblock`)
  return data
}

export async function fetchThresholds() {
  // GET /api/config/thresholds
  const { data } = await api.get('/api/config/thresholds')
  return data
}

export async function saveThresholds(values) {
  // PUT /api/config/thresholds
  const { data } = await api.put('/api/config/thresholds', values)
  return data
}

// WebSocket real-time traffic (thay cho polling ở TrafficChart):
// const ws = connectTrafficSocket((point) => { ...cập nhật state... })
export function connectTrafficSocket(onPoint) {
  const base = (import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000')
  const ws = new WebSocket(`${base}/ws/traffic`)
  ws.onmessage = (evt) => {
    try {
      onPoint(JSON.parse(evt.data))
    } catch {
      // bỏ qua khung dữ liệu lỗi định dạng
    }
  }
  return ws
}
