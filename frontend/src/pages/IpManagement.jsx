import { useEffect, useState } from 'react'
import IpTable from '../components/IpTable'
import { getBlockedIps } from '../services/api'

// Trang quản lý IP:
// - Khối trên: đấu nối trực tiếp GET /api/blocked-ips (services/api.js) để hiển thị
//   đúng danh sách IP đang bị Zero-Trust Enforcer chặn trên Firewall.
// - Khối dưới: giữ nguyên bảng đầy đủ (rows truyền từ App.jsx) để bật/tắt chặn thủ công.
function IpManagement({ rows, onToggleBlock }) {
  const [blockedRows, setBlockedRows] = useState(null) // null = đang tải / chưa có dữ liệu từ API
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    getBlockedIps()
      .then((data) => {
        if (!cancelled) setBlockedRows(Array.isArray(data) ? data : [])
      })
      .catch(() => {
        if (!cancelled) setError('Không gọi được /api/blocked-ips (Backend chưa chạy?). Đang hiển thị dữ liệu cục bộ.')
      })

    return () => {
      cancelled = true
    }
  }, [])

  // Fallback khi API lỗi/chưa chạy: lọc blocked=true từ dữ liệu đã có trong App.jsx.
  const fallbackBlocked = rows.filter((r) => r.blocked)
  const displayedBlocked = blockedRows ?? fallbackBlocked

  return (
    <>
      <div className="panel-header" style={{ marginBottom: 8 }}>
        <div>
          <h3>IP đã bị khóa (GET /api/blocked-ips)</h3>
          {error && <p className="panel-sub">{error}</p>}
        </div>
      </div>
      <IpTable rows={displayedBlocked} onToggleBlock={onToggleBlock} compact />

      <div className="panel-header" style={{ marginTop: 24, marginBottom: 8 }}>
        <div>
          <h3>Toàn bộ IP đang theo dõi</h3>
        </div>
      </div>
      <IpTable rows={rows} onToggleBlock={onToggleBlock} />
    </>
  )
}

export default IpManagement
