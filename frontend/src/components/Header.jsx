import { memo, useEffect, useState } from 'react'
import { Search, Bell } from 'lucide-react'
import './Header.css'

// Đồng hồ tách riêng: mỗi giây chỉ render lại đúng khối này, không đụng tới thanh tìm kiếm.
function Clock() {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  const time = now.toLocaleTimeString('vi-VN', { hour12: false })
  const date = now.toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' })

  return (
    <div className="header-clock">
      <span className="header-clock-time">{time}</span>
      <span className="header-clock-date">{date}</span>
    </div>
  )
}

const TITLES = {
  overview: 'Tổng quan hệ thống',
  traffic: 'Giám sát lưu lượng',
  alerts: 'Cảnh báo NIDS',
  ips: 'Quản lý IP',
  attacklab: 'Attack Lab',
  config: 'Cấu hình ngưỡng phát hiện',
}

function Header({ view = 'overview', query = '', onQuery, connected = false, alertCount = 0, onBell }) {
  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">{TITLES[view] ?? TITLES.overview}</h1>
        <span className={`status-pill${connected ? '' : ' is-off'}`} role="status">
          <span className="pulse-dot" />
          <span className="status-text">{connected ? 'Realtime kết nối' : 'Mất kết nối realtime'}</span>
        </span>
      </div>

      <div className="header-right">
        <label className="header-search">
          <Search size={15} strokeWidth={2} aria-hidden="true" />
          <input
            type="text"
            value={query}
            onChange={(e) => onQuery?.(e.target.value)}
            placeholder="Lọc theo IP, loại tấn công, giao thức..."
            aria-label="Lọc theo IP, loại tấn công, giao thức"
          />
        </label>

        <button type="button" className="header-icon-btn" aria-label="Xem cảnh báo" onClick={onBell}>
          <Bell size={17} strokeWidth={2} />
          {alertCount > 0 && <span className="header-icon-dot" />}
        </button>

        <Clock />
      </div>
    </header>
  )
}

export default memo(Header)
