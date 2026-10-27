import { useEffect, useState } from 'react'
import { RefreshCw, ShieldOff } from 'lucide-react'
import { getBlockedIps, unblockIpFirewall } from '../services/api'
import './IPManagement.css'

const POLL_MS = 7000

// Component độc lập (mục 3 trong mô tả đề tài): tự gọi GET /api/blocked-ips
// để liệt kê các IP đang bị chặn, và bắn POST /api/firewall/unblock khi bấm
// "Unblock" để Backend gọi netsh advfirewall gỡ rule thật trên Windows
// Defender Firewall. Khác với components/IpTable.jsx (nhận rows/callback từ
// App.jsx) — component này tự quản lý state + gọi API riêng.
function IPManagement() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pendingIp, setPendingIp] = useState(null)
  const [reloadTick, setReloadTick] = useState(0)

  useEffect(() => {
    let cancelled = false

    getBlockedIps()
      .then((data) => {
        if (cancelled) return
        setRows(Array.isArray(data) ? data : [])
        setError(null)
      })
      .catch(() => {
        if (cancelled) return
        setError('Không gọi được /api/blocked-ips (Backend chưa chạy?).')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [reloadTick])

  useEffect(() => {
    const id = setInterval(() => setReloadTick((n) => n + 1), POLL_MS)
    return () => clearInterval(id)
  }, [])

  async function handleUnblock(ip) {
    setPendingIp(ip)
    const prevRows = rows
    // Cập nhật lạc quan: gỡ IP khỏi danh sách ngay trên UI trước.
    setRows((prev) => prev.filter((r) => r.ip !== ip))
    try {
      await unblockIpFirewall(ip)
    } catch {
      // Lỗi gọi API -> khôi phục lại danh sách cũ, không để UI "nói dối".
      setRows(prevRows)
      setError(`Không gỡ được ${ip} (kiểm tra Backend / quyền Administrator cho netsh).`)
    } finally {
      setPendingIp(null)
    }
  }

  return (
    <div className="panel ip-mgmt-panel">
      <div className="panel-header">
        <div>
          <h3>Quản lý IP bị chặn</h3>
          <p className="panel-sub">
            Nguồn: GET /api/blocked-ips · Unblock: POST /api/firewall/unblock
          </p>
        </div>
        <button type="button" className="ip-mgmt-refresh" onClick={() => setReloadTick((n) => n + 1)}>
          <RefreshCw size={13} strokeWidth={2} />
          Làm mới
        </button>
      </div>

      {error && <p className="ip-mgmt-error">{error}</p>}

      <div className="ip-mgmt-scroll">
        <table className="ip-mgmt-table">
          <thead>
            <tr>
              <th>Địa chỉ IP</th>
              <th>Giao thức / Loại tấn công</th>
              <th>Số gói tin</th>
              <th>Phát hiện lúc</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.ip}>
                <td className="ip-cell">{row.ip}</td>
                <td className="mono-cell">{row.proto}</td>
                <td className="mono-cell">{row.packets?.toLocaleString('vi-VN')}</td>
                <td className="dim-cell">{row.lastSeen}</td>
                <td>
                  <button
                    type="button"
                    className="ip-mgmt-unblock-btn"
                    disabled={pendingIp === row.ip}
                    onClick={() => handleUnblock(row.ip)}
                  >
                    <ShieldOff size={13} strokeWidth={2} />
                    {pendingIp === row.ip ? 'Đang gỡ...' : 'Unblock'}
                  </button>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={5} className="ip-mgmt-empty">
                  Không có IP nào đang bị chặn.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default IPManagement
