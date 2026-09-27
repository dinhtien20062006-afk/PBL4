// Dữ liệu mẫu dùng chung cho toàn bộ Dashboard.
// Khi backend (FastAPI + MySQL) sẵn sàng, thay các hàm "seed*"/"makeMock*"
// bằng lệnh gọi tương ứng trong src/api/client.js — các component không cần
// đổi cấu trúc, chỉ đổi nguồn dữ liệu.

export const SEED_ALERTS = [
  { id: 'a1', ip: '203.0.113.44', type: 'SYN Flood', port: 25, sev: 'high', time: '2 phút trước' },
  { id: 'a2', ip: '198.51.100.9', type: 'Brute-force POP3', port: 110, sev: 'med', time: '11 phút trước' },
  { id: 'a3', ip: '192.0.2.171', type: 'Spam Mail (SMTP)', port: 25, sev: 'med', time: '26 phút trước' },
  { id: 'a4', ip: '203.0.113.201', type: 'Brute-force SMTP', port: 25, sev: 'high', time: '40 phút trước' },
  { id: 'a5', ip: '198.51.100.63', type: 'SYN Flood', port: 110, sev: 'low', time: '1 giờ trước' },
]

export const SEED_IPS = [
  { ip: '192.168.1.14', status: 'normal', proto: 'TCP', packets: 1284, lastSeen: '2 giây trước', blocked: false },
  { ip: '10.0.0.82', status: 'suspicious', proto: 'TCP', packets: 9531, lastSeen: '5 giây trước', blocked: false },
  { ip: '172.16.4.201', status: 'normal', proto: 'UDP', packets: 402, lastSeen: '11 giây trước', blocked: false },
  { ip: '203.0.113.55', status: 'suspicious', proto: 'TCP', packets: 22890, lastSeen: '32 giây trước', blocked: true },
  { ip: '192.168.1.27', status: 'normal', proto: 'ICMP', packets: 88, lastSeen: '1 phút trước', blocked: false },
  { ip: '198.51.100.9', status: 'suspicious', proto: 'TCP', packets: 5120, lastSeen: '1 phút trước', blocked: false },
]

export const SEED_THRESHOLDS = {
  spamPerMinute: 50,
  bruteForceAttempts: 5,
  synPacketsPerSecond: 200,
  blockDurationSeconds: 900,
}

// TODO(backend): thay bằng GET /api/traffic/protocols
export function makeMockProtocolSplit() {
  const tcp = 55 + Math.round(Math.random() * 15)
  const udp = 20 + Math.round(Math.random() * 10)
  const icmp = Math.max(3, 100 - tcp - udp)
  return [
    { label: 'TCP', value: tcp, color: '#3aa8e0' },
    { label: 'UDP', value: udp, color: '#35c98f' },
    { label: 'ICMP', value: icmp, color: '#e0a83a' },
  ]
}

// TODO(backend): thay bằng GET /api/traffic/ports (lọc theo cổng Mail 25/110)
export function makeMockPortActivity() {
  return [
    { label: 'SMTP · 25', value: 40 + Math.round(Math.random() * 60) },
    { label: 'POP3 · 110', value: 15 + Math.round(Math.random() * 30) },
    { label: 'Khác', value: 10 + Math.round(Math.random() * 20) },
  ]
}

// TODO(backend): thay bằng GET /api/traffic/top-sources
export function makeMockTopSources() {
  return [...SEED_IPS]
    .sort((a, b) => b.packets - a.packets)
    .slice(0, 5)
}
