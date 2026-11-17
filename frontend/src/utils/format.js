// Backend trả datetime ISO không timezone (giờ local của máy chủ).
export function formatTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString('vi-VN')
}

export const formatNumber = (n, digits = 0) =>
  Number(n ?? 0).toLocaleString('vi-VN', { maximumFractionDigits: digits })

// `now` được truyền vào từ hook useNow() để nhãn "x giây trước" tự cập nhật
// mà không cần tải lại dữ liệu từ server.
export function timeAgo(value, now = Date.now()) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  const s = Math.max(0, Math.round((now - d.getTime()) / 1000))
  if (s < 60) return `${s} giây trước`
  if (s < 3600) return `${Math.floor(s / 60)} phút trước`
  if (s < 86400) return `${Math.floor(s / 3600)} giờ trước`
  return `${Math.floor(s / 86400)} ngày trước`
}

export function isRecent(value, now, windowMs = 60_000) {
  const t = new Date(value).getTime()
  return !Number.isNaN(t) && now - t < windowMs
}

const SEV = { critical: 'high', high: 'high', medium: 'med', low: 'low' }

// alert_history -> dạng AlertFeed / AlertCard.
// Không lưu sẵn chuỗi thời gian: component tự tính từ createdAt để luôn mới.
export function mapAlert(a) {
  return {
    id: a.id,
    ip: a.source_ip,
    type: a.attack_type,
    value: a.threshold_value,
    sev: SEV[String(a.severity || '').toLowerCase()] || 'low',
    createdAt: a.created_at,
  }
}

// /api/ips -> dạng IpTable
export function mapIp(r) {
  return {
    ip: r.ip,
    status: r.status,
    proto: r.proto,
    packets: r.packets,
    lastSeen: r.last_seen,
    blocked: r.blocked,
  }
}
