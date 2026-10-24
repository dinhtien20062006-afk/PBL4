import { useEffect, useRef, useState } from 'react'
import { Radio } from 'lucide-react'
import { fetchRecentLogs } from '../api/client'
import './TrafficTable.css'

const PROTOCOLS = ['TCP', 'UDP', 'ICMP']
const POLL_INTERVAL_MS = 2000
const ROW_LIMIT = 12

// Dùng khi Backend (GET /api/logs/recent) chưa chạy, để UI vẫn có dữ liệu
// xem trước. Khi nids_engine/sniffer.py + API ghi log thật hoạt động, nhánh
// này sẽ không còn được gọi tới (xem fetchRows() bên dưới).
function randomIp() {
  return Array.from({ length: 4 }, () => Math.floor(Math.random() * 255) + 1).join('.')
}

function randomMockRow() {
  return {
    id: `${Date.now()}-${Math.random()}`,
    src_ip: randomIp(),
    dst_ip: randomIp(),
    port: 1024 + Math.floor(Math.random() * 60000),
    protocol: PROTOCOLS[Math.floor(Math.random() * PROTOCOLS.length)],
    time: 'vừa xong',
  }
}

// Bảng lưu lượng mạng thời gian thực: IP nguồn, IP đích, Cổng, Giao thức.
// Gọi GET /api/logs/recent qua axios và polling bằng setInterval mỗi
// POLL_INTERVAL_MS — giải pháp tạm thời cho tới khi tích hợp WebSocket
// (xem connectTrafficSocket trong src/api/client.js) để đẩy dữ liệu real-time
// thay vì polling.
function TrafficTable() {
  const [rows, setRows] = useState(() => Array.from({ length: 8 }, randomMockRow))
  const [apiOnline, setApiOnline] = useState(false)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true

    async function poll() {
      try {
        const data = await fetchRecentLogs(ROW_LIMIT)
        if (!mountedRef.current) return
        if (Array.isArray(data) && data.length > 0) {
          setRows(data.slice(0, ROW_LIMIT))
          setApiOnline(true)
          return
        }
        setApiOnline(true)
      } catch {
        // Backend chưa chạy / lỗi mạng -> tiếp tục hiển thị dữ liệu mẫu,
        // không chặn UI, và thử lại ở lần poll tiếp theo.
        if (!mountedRef.current) return
        setApiOnline(false)
        setRows((prev) => [randomMockRow(), ...prev].slice(0, ROW_LIMIT))
      }
    }

    poll()
    const id = setInterval(poll, POLL_INTERVAL_MS)
    return () => {
      mountedRef.current = false
      clearInterval(id)
    }
  }, [])

  return (
    <div className="panel traffic-table-panel">
      <div className="panel-header">
        <div>
          <h3>Bảng lưu lượng mạng</h3>
          <p className="panel-sub">GET /api/logs/recent · poll {POLL_INTERVAL_MS / 1000}s</p>
        </div>
        <span className={`traffic-table-status ${apiOnline ? 'is-live' : 'is-demo'}`}>
          <Radio size={12} strokeWidth={2.2} />
          {apiOnline ? 'Live' : 'Demo'}
        </span>
      </div>

      <div className="traffic-table-scroll">
        <table className="traffic-table">
          <thead>
            <tr>
              <th>IP nguồn</th>
              <th>IP đích</th>
              <th>Cổng</th>
              <th>Giao thức</th>
              <th>Thời điểm</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id ?? `${row.src_ip}-${row.dst_ip}-${row.port}`}>
                <td className="mono-cell">{row.src_ip}</td>
                <td className="mono-cell">{row.dst_ip}</td>
                <td className="mono-cell">{row.port}</td>
                <td>
                  <span className={`proto-badge proto-${(row.protocol || '').toLowerCase()}`}>
                    {row.protocol}
                  </span>
                </td>
                <td className="dim-cell">{row.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default TrafficTable
