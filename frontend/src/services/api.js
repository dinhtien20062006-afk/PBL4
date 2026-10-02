import axios from 'axios'

// Client axios dùng chung cho toàn bộ service trong thư mục này.
// Đổi VITE_API_BASE_URL trong .env khi deploy (mặc định trỏ về FastAPI chạy local).
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 5000,
})

/**
 * GET /api/blocked-ips
 * Trả về danh sách các IP đã bị Zero-Trust Enforcer chặn trên Windows Firewall.
 * Cấu trúc mỗi phần tử khớp với IpTable.jsx:
 *   { ip, status, proto, packets, lastSeen, blocked }
 */
export async function getBlockedIps() {
  const { data } = await apiClient.get('/api/blocked-ips')
  return data
}

/**
 * GET /api/ips
 * Toàn bộ IP đang được NIDS theo dõi (bình thường + nghi ngờ + đã chặn).
 */
export async function getIps() {
  const { data } = await apiClient.get('/api/ips')
  return data
}

/**
 * POST /api/ips/{ip}/block  và  POST /api/ips/{ip}/unblock
 */
export async function blockIpAddress(ip) {
  const { data } = await apiClient.post(`/api/ips/${ip}/block`)
  return data
}

export async function unblockIpAddress(ip) {
  const { data } = await apiClient.post(`/api/ips/${ip}/unblock`)
  return data
}

export default apiClient
