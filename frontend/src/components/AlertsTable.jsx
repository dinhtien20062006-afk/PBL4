import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { fetchRecentAlerts } from '../api/client'
import { SEED_ALERTS } from '../data/mockData'
import './AlertsTable.css'

const POLL_MS = 5000

// Màu trạng thái trực quan theo loại tấn công (mục 2 trong mô tả đề tài):
// Đỏ = DoS/SYN Flood, Cam = Brute-force, Xanh dương = các loại khác (Spam...).
function severityFor(type = '') {
  const t = type.toLowerCase()
  if (t.includes('syn') || t.includes('flood') || t.includes('dos')) {
    return { cls: 'row-red', label: 'DoS / SYN Flood' }
  }
  if (t.includes('brute')) {
    return { cls: 'row-orange', label: 'Brute-force' }
  }
  return { cls: 'row-blue', label: 'Khác' }
}

// Component độc lập: tự gọi GET /api/alerts/recent qua axios (api/client.js)
// và tự poll định kỳ — không phụ thuộc state từ App.jsx như AlertFeed.jsx.
function AlertsTable() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [liveApi, setLiveApi] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [reloadTick, setReloadTick] = useState(0)

  // Theo đúng khuôn mẫu đã dùng ở App.jsx: gọi hàm axios trong client.js rồi
  // xử lý setState trong .then()/.catch(), không gọi qua một hàm nội bộ
  // trung gian — tránh cascading render trong effect.
  useEffect(() => {
    let cancelled = false

    fetchRecentAlerts(20)
      .then((data) => {
        if (cancelled) return
        if (Array.isArray(data) && data.length > 0) {
          setAlerts(data)
          setLiveApi(true)
        } else {
          setAlerts((prev) => (prev.length > 0 ? prev : SEED_ALERTS))
        }
      })
      .catch(() => {
        // Backend /api/alerts/recent chưa sẵn sàng -> dùng dữ liệu mẫu, không chặn UI.
        if (cancelled) return
        setLiveApi(false)
        setAlerts((prev) => (prev.length > 0 ? prev : SEED_ALERTS))
      })
      .finally(() => {
        if (cancelled) return
        setLoading(false)
        setLastUpdated(new Date())
      })

    return () => {
      cancelled = true
    }
  }, [reloadTick])

  useEffect(() => {
    const id = setInterval(() => setReloadTick((n) => n + 1), POLL_MS)
    return () => clearInterval(id)
  }, [])

  function handleRefresh() {
    setReloadTick((n) => n + 1)
  }

  return (
    <div className="panel alerts-table-panel">
      <div className="panel-header">
        <div>
          <h3>Bảng cảnh báo (Alerts Table)</h3>
          <p className="panel-sub">
            Nguồn: GET /api/alerts/recent {liveApi ? '· đang kết nối Backend' : '· dữ liệu mẫu (demo)'}
          </p>
        </div>
        <button type="button" className="alerts-table-refresh" onClick={handleRefresh}>
          <RefreshCw size={13} strokeWidth={2} />
          Làm mới
        </button>
      </div>

      <div className="alerts-table-scroll">
        <table className="alerts-table">
          <thead>
            <tr>
              <th>Thời gian</th>
              <th>IP nguồn</th>
              <th>Loại tấn công</th>
              <th>Cổng</th>
              <th>Trạng thái</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => {
              const sev = severityFor(a.type)
              return (
                <tr key={a.id} className={sev.cls}>
                  <td className="mono">{a.time}</td>
                  <td className="mono">{a.ip}</td>
                  <td>{a.type}</td>
                  <td className="mono">{a.port}</td>
                  <td>
                    <span className={`badge ${sev.cls}`}>{sev.label}</span>
                  </td>
                </tr>
              )
            })}
            {!loading && alerts.length === 0 && (
              <tr>
                <td colSpan={5} className="alerts-table-empty">
                  Chưa có cảnh báo nào được ghi nhận.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {lastUpdated && (
        <p className="alerts-table-updated">
          Cập nhật lần cuối: {lastUpdated.toLocaleTimeString('vi-VN')}
        </p>
      )}
    </div>
  )
}

export default AlertsTable
