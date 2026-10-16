import { Gauge, Ban, Siren } from 'lucide-react'
import StatCard from './StatCard'
import './StatCards.css'

// Nhóm 3 thẻ KPI tổng quan cho Dashboard: tổng traffic (pps), số IP đang bị
// Zero-Trust Enforcer chặn, và số cảnh báo NIDS đang mở. Nhận dữ liệu đã
// tính sẵn từ App.jsx/Dashboard.jsx qua props để không phải tự gọi API ở
// đây — chỗ gọi API thật (GET /api/traffic/summary, /api/alerts, /api/ips)
// nằm ở App.jsx theo đúng luồng "nguồn sự thật" chung của toàn bộ Dashboard.
//
// Props:
//   trafficPerSecond : number | string  — gói tin / giây hiện tại
//   trafficDelta      : string | null    — ví dụ "+4.2%" so với phút trước
//   blockedCount      : number           — số IP đã bị chặn
//   alertsCount       : number           — số cảnh báo đang mở
function StatCards({ trafficPerSecond = 0, trafficDelta, blockedCount = 0, alertsCount = 0 }) {
  const cards = [
    {
      icon: Gauge,
      label: 'Tổng traffic (gói/giây)',
      value: String(trafficPerSecond),
      delta: trafficDelta,
      tone: 'info',
    },
    {
      icon: Ban,
      label: 'Số IP đang bị chặn',
      value: String(blockedCount),
      tone: 'crit',
    },
    {
      icon: Siren,
      label: 'Số cảnh báo đang mở',
      value: String(alertsCount),
      tone: 'warn',
    },
  ]

  return (
    <div className="stat-cards-grid">
      {cards.map((card) => (
        <StatCard key={card.label} {...card} />
      ))}
    </div>
  )
}

export default StatCards
