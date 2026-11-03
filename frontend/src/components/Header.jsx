import { useEffect, useState } from 'react'
import { Search, Bell } from 'lucide-react'
import './Header.css'

function useClock() {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])
  return now
}

const TITLES = {
  overview: 'Tổng quan hệ thống',
  traffic: 'Giám sát lưu lượng',
  alerts: 'Cảnh báo NIDS',
  ips: 'Quản lý IP',
  attacklab: 'Attack Lab',
  config: 'Cấu hình ngưỡng phát hiện',
}

function Header({ view = 'overview' }) {
  const now = useClock()
  const time = now.toLocaleTimeString('vi-VN', { hour12: false })
  const date = now.toLocaleDateString('vi-VN', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
  })

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">{TITLES[view] ?? TITLES.overview}</h1>
        <span className="status-pill">
          <span className="pulse-dot" />
          Zero-Trust Active
        </span>
      </div>

      <div className="header-right">
        <div className="header-search">
          <Search size={15} strokeWidth={2} />
          <input type="text" placeholder="Tìm theo IP, cổng, giao thức..." />
        </div>

        <button type="button" className="header-icon-btn" aria-label="Thông báo">
          <Bell size={16} strokeWidth={2} />
          <span className="header-icon-dot" />
        </button>

        <div className="header-clock">
          <span className="header-clock-time">{time}</span>
          <span className="header-clock-date">{date}</span>
        </div>
      </div>
    </header>
  )
}

export default Header
