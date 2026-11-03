// Backend trả datetime dạng "2026-11-02T13:28:22" (giờ local, không có timezone)
export function formatTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString('vi-VN')
}

export function timeAgo(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  const s = Math.max(0, Math.round((Date.now() - d.getTime()) / 1000))
  if (s < 60) return `${s} giây trước`
  if (s < 3600) return `${Math.floor(s / 60)} phút trước`
  if (s < 86400) return `${Math.floor(s / 3600)} giờ trước`
  return `${Math.floor(s / 86400)} ngày trước`
}

const SEV = { high: 'high', medium: 'med', low: 'low' }

// Dòng trong bảng alerts -> dạng AlertFeed đang dùng
export function mapAlert(a) {
  return {
    id: a.id,
    ip: a.source_ip,
    type: a.attack_type,
    port: a.port ?? '—',
    sev: SEV[String(a.severity || '').toLowerCase()] || 'low',
    time: timeAgo(a.created_at),
  }
}

// Dòng /api/ips -> dạng IpTable đang dùng
export function mapIp(r) {
  return {
    ip: r.ip,
    status: r.status,
    proto: r.proto,
    packets: r.packets,
    lastSeen: timeAgo(r.last_seen),
    blocked: r.blocked,
  }
}
